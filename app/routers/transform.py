from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging
import uuid

from app.database.session import get_db
from app.services.field_mapping_service import FieldMappingService
from app.services.metadata_service import MetadataService
from app.services.config_service import ConfigService
from app.core.exceptions import TransformationError

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/dialpad-to-ssot", status_code=status.HTTP_200_OK)
async def transform_dialpad_to_ssot(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Transform Dialpad data to SSOT format
    
    This endpoint accepts transformation requests with:
    - Job type ID for the transformation
    - Dialpad data to transform
    
    Returns transformed SSOT data
    """
    logger.info(f"Received Dialpad to SSOT transform request")
    
    try:
        job_type_id = request.get("job_type_id")
        dialpad_data = request.get("data", {})
        
        if not job_type_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required parameter: job_type_id"
            )
        
        if not dialpad_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required parameter: data"
            )
        
        # Initialize services
        field_mapping_service = FieldMappingService(db)
        metadata_service = MetadataService()
        config_service = ConfigService(db)
        
        # Get field mappings for job type to determine target entity dynamically
        mappings = field_mapping_service.get_mappings_for_job_type(job_type_id)
        if not mappings:
            raise ValueError(f"No field mappings found for job type ID {job_type_id}")
        
        # Extract target entity from field mappings (all mappings for a job type should have same target_entity)
        target_entity = mappings[0].target_entity if mappings else "unknown"
        
        # Apply field mappings
        mapped_fields, unmapped_metadata, transformation_info = field_mapping_service.apply_field_mappings(
            dialpad_data, mappings
        )
        
        # Generate entity ID
        source_id = dialpad_data.get("id") or str(uuid.uuid4())
        entity_id = f"ssot_{target_entity}_{source_id}"
        
        # Create SSOT data structure
        ssot_data = metadata_service.format_ssot_data(
            entity_type=target_entity,
            entity_id=entity_id,
            job_type_id=job_type_id,
            source_platform="dialpad",
            mapped_fields=mapped_fields,
            unmapped_metadata=unmapped_metadata,
            transformation_info=transformation_info
        )
        
        return {
            "status": "success",
            "message": f"Transformation to SSOT completed for job_type_id: {job_type_id}",
            "ssot_data": ssot_data
        }
    
    except TransformationError as e:
        logger.error(f"Transformation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transformation error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transforming data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error transforming data: {str(e)}"
        )


@router.post("/test-field-mapping", status_code=status.HTTP_200_OK)
async def test_field_mapping(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Test field mapping for a specific job type with sample data
    
    This endpoint accepts:
    - Job type ID for the transformation
    - Sample data to transform
    
    Returns mapped fields and unmapped metadata
    """
    logger.info(f"Received test field mapping request")
    
    try:
        job_type_id = request.get("job_type_id")
        sample_data = request.get("data", {})
        
        if not job_type_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required parameter: job_type_id"
            )
        
        if not sample_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required parameter: data"
            )
        
        # Initialize field mapping service
        field_mapping_service = FieldMappingService(db)
        
        # Get field mappings for job type
        mappings = field_mapping_service.get_mappings_for_job_type(job_type_id)
        if not mappings:
            raise ValueError(f"No field mappings found for job type ID {job_type_id}")
        
        # Apply field mappings
        mapped_fields, unmapped_metadata, transformation_info = field_mapping_service.apply_field_mappings(
            sample_data, mappings
        )
        
        return {
            "status": "success",
            "job_type_id": job_type_id,
            "mapped_fields": mapped_fields,
            "unmapped_metadata": unmapped_metadata,
            "transformation_info": transformation_info
        }
    
    except Exception as e:
        logger.error(f"Error testing field mapping: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing field mapping: {str(e)}"
        )