import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

from app.database.session import get_db
from app.database.models import MCPRequest as MCPRequestModel
from app.core.exceptions import TransformationError
from app.services.field_mapping_service import FieldMappingService
from app.services.metadata_service import MetadataService
from app.services.config_service import ConfigService

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/transform", status_code=status.HTTP_200_OK)
async def transform_data(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    MCP endpoint for transforming data
    
    This endpoint accepts transformation requests with:
    - Job type ID for the transformation
    - Source platform
    - Data to transform
    
    Returns transformed SSOT data
    """
    logger.info(f"Received transform request: {request}")
    
    try:
        # Handle raw MCP payload
        if "method" in request and "params" in request:
            method = request["method"]
            params = request["params"]
            
            if method == "transform_to_ssot":
                # Dialpad → SSOT transformation
                job_type_id = params.get("job_type_id")
                source_platform = params.get("source_platform", "dialpad")
                source_data = params.get("source_data", {})
                
                # Initialize services
                field_mapping_service = FieldMappingService(db)
                metadata_service = MetadataService()
                config_service = ConfigService(db)
                
                # Get job type configuration
                job_type_config = config_service.get_job_type_config(job_type_id)
                if not job_type_config:
                    raise ValueError(f"Job type ID {job_type_id} not found")
                
                # Get field mappings for job type to determine target entity dynamically
                mappings = field_mapping_service.get_mappings_for_job_type(job_type_id)
                if not mappings:
                    raise ValueError(f"No field mappings found for job type ID {job_type_id}")
                
                # Extract target entity from field mappings (all mappings for a job type should have same target_entity)
                target_entity = mappings[0].target_entity if mappings else "unknown"
                
                # Apply field mappings
                mapped_fields, unmapped_metadata, transformation_info = field_mapping_service.apply_field_mappings(
                    source_data, mappings
                )
                
                # Generate entity ID
                source_id = source_data.get("id") or str(uuid.uuid4())
                entity_id = f"ssot_{target_entity}_{source_id}"
                
                # Create SSOT data structure
                ssot_data = metadata_service.format_ssot_data(
                    entity_type=target_entity,
                    entity_id=entity_id,
                    job_type_id=job_type_id,
                    source_platform=source_platform,
                    mapped_fields=mapped_fields,
                    unmapped_metadata=unmapped_metadata,
                    transformation_info=transformation_info
                )
                
                # Generate a unique request ID
                request_id = str(uuid.uuid4())
                
                # Create a new MCP request record
                mcp_request = MCPRequestModel(
                    request_id=request_id,
                    operation="transform_to_ssot",
                    parameters={
                        "job_type_id": job_type_id,
                        "source_platform": source_platform,
                        "entity_type": target_entity
                    },
                    status="completed"
                )
                
                # Save to database
                db.add(mcp_request)
                db.commit()
                
                return {
                    "request_id": request_id,
                    "status": "completed",
                    "message": f"Transformation to SSOT completed for job_type_id: {job_type_id}",
                    "details": {
                        "ssot_data": ssot_data,
                        "job_type_id": job_type_id,
                        "source_platform": source_platform,
                        "target_entity": target_entity
                    }
                }
            elif method == "transform_raw":
                # Dialpad microservice no longer handles raw transformations to other platforms
                # This is now handled by the target platform microservices (e.g., Zoom microservice)
                raise ValueError(f"Raw transformations are no longer supported in Dialpad microservice. Please use the target platform microservice.")
            else:
                raise ValueError(f"Unsupported MCP method: {method}")
        else:
            raise ValueError("Invalid MCP request format - missing method and params")
    
    except TransformationError as e:
        logger.error(f"Transformation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transformation error: {str(e)}"
        )
    except Exception as e:
        import traceback
        logger.error(f"Error transforming data: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error transforming data: {str(e)}"
        )


@router.get("/field-mappings/{job_type_id}")
async def get_field_mappings(
    job_type_id: int,
    db: Session = Depends(get_db)
):
    """
    Get field mappings for a specific job type
    
    Returns:
        List of field mappings
    """
    try:
        # Query field mappings for job type
        field_mapping_service = FieldMappingService(db)
        mappings = field_mapping_service.get_mappings_for_job_type(job_type_id)
        
        # Format the mappings for response
        formatted_mappings = []
        for mapping in mappings:
            formatted_mappings.append({
                "job_type_id": mapping.job_type_id,
                "source_platform": mapping.source_platform,
                "target_entity": mapping.target_entity,
                "ssot_field": mapping.ssot_field,
                "source_field": mapping.source_field,
                "transformation_rule": mapping.transformation_rule,
                "is_required": mapping.is_required,
                "description": mapping.description
            })
        
        return {
            "job_type_id": job_type_id,
            "mapping_count": len(formatted_mappings),
            "mappings": formatted_mappings
        }
    
    except Exception as e:
        logger.error(f"Error retrieving field mappings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving field mappings: {str(e)}"
        )


@router.get("/job-types")
async def get_job_types(
    db: Session = Depends(get_db)
):
    """
    Get all supported job types
    
    Returns:
        List of job types
    """
    try:
        # Query job types
        config_service = ConfigService(db)
        
        # For now, return hardcoded job types
        job_types = [
            {
                "id": 60,
                "code": "dialpad_users",
                "name": "Dialpad Users",
                "description": "Transform Dialpad users to SSOT person entities",
                "source_platform_id": 5,  # Assuming 5 is Dialpad
                "target_entity": "person"
            },
            {
                "id": 61,
                "code": "dialpad_sites",
                "name": "Dialpad Sites",
                "description": "Transform Dialpad sites to SSOT location entities",
                "source_platform_id": 5,  # Assuming 5 is Dialpad
                "target_entity": "location"
            },
            {
                "id": 62,
                "code": "dialpad_call_queues",
                "name": "Dialpad Call Queues",
                "description": "Transform Dialpad call queues to SSOT call_group entities",
                "source_platform_id": 5,  # Assuming 5 is Dialpad
                "target_entity": "call_group"
            },
            {
                "id": 63,
                "code": "dialpad_auto_receptionists",
                "name": "Dialpad Auto Receptionists",
                "description": "Transform Dialpad auto receptionists to SSOT auto_attendant entities",
                "source_platform_id": 5,  # Assuming 5 is Dialpad
                "target_entity": "auto_attendant"
            }
        ]
        
        return {
            "job_type_count": len(job_types),
            "job_types": job_types
        }
    
    except Exception as e:
        logger.error(f"Error retrieving job types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving job types: {str(e)}"
        )