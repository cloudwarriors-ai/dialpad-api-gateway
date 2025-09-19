from typing import Dict, Any, List
import logging
from datetime import datetime
import uuid

from app.services.field_mapping_service import FieldMappingService
from app.services.metadata_service import MetadataService
from app.core.exceptions import TransformationError

# Configure logging
logger = logging.getLogger(__name__)


class DialpadToSSOTSitesTransformer:
    """
    Transform Dialpad site data to SSOT Location entity using field mappings
    """
    
    def __init__(self, db, field_mapping_service=None, metadata_service=None):
        """
        Initialize the transformer with services
        
        Args:
            db: Database session
            field_mapping_service: Field mapping service (optional)
            metadata_service: Metadata service (optional)
        """
        self.db = db
        self.field_mapping_service = field_mapping_service or FieldMappingService(db)
        self.metadata_service = metadata_service or MetadataService()
    
    def transform(self, dialpad_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Dialpad site data to SSOT Location entity
        
        Args:
            dialpad_data: Dialpad site data
            
        Returns:
            SSOT Location entity data
        """
        try:
            # Job type ID for Dialpad Sites → SSOT Location
            job_type_id = 61
            
            # Load field mappings for JobType 61
            mappings = self.field_mapping_service.get_mappings_for_job_type(job_type_id)
            
            if not mappings:
                logger.error(f"No field mappings found for job type ID {job_type_id}")
                raise TransformationError(f"No field mappings found for job type ID {job_type_id}")
            
            # Apply field mappings
            mapped_fields, unmapped_metadata, transformation_info = self.field_mapping_service.apply_field_mappings(
                dialpad_data, mappings
            )
            
            # Construct SSOT format
            source_id = dialpad_data.get("office_id") or str(uuid.uuid4())
            entity_id = f"ssot_location_{source_id}"
            
            ssot_data = {
                "entity_type": "location",
                "entity_id": entity_id,
                "job_type_id": job_type_id,
                "source_platform": "dialpad",
                "mapped_fields": mapped_fields,
                "unmapped_metadata": unmapped_metadata,
                "transformation_info": transformation_info
            }
            
            return ssot_data
        
        except Exception as e:
            logger.error(f"Error transforming Dialpad site data: {str(e)}")
            raise TransformationError(f"Error transforming Dialpad site data: {str(e)}")
            
    def extract_location_data(self, ssot_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract location data from SSOT data
        
        Args:
            ssot_data: SSOT data
            
        Returns:
            Location data
        """
        return self.metadata_service.extract_entity_data(ssot_data, "location")