from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class MetadataService:
    """
    Service for handling metadata for unmapped fields
    """
    
    def create_metadata(self, unmapped_fields: Dict[str, Any], source_platform: str) -> Dict[str, Any]:
        """
        Create metadata for unmapped fields
        
        Args:
            unmapped_fields: Dictionary of unmapped fields
            source_platform: Source platform name
            
        Returns:
            Metadata dictionary
        """
        metadata = {}
        
        for field, value in unmapped_fields.items():
            metadata[field] = {
                "value": value,
                "description": f"Unmapped {source_platform} field"
            }
        
        return metadata
    
    def merge_metadata(self, existing_metadata: Dict[str, Any], new_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge existing metadata with new metadata
        
        Args:
            existing_metadata: Existing metadata dictionary
            new_metadata: New metadata dictionary
            
        Returns:
            Merged metadata dictionary
        """
        merged = existing_metadata.copy()
        
        for field, value in new_metadata.items():
            if field in merged:
                # Field already exists in metadata, update with new value
                merged[field]["value"] = value["value"]
                # Keep existing description if available
                if "description" not in merged[field] and "description" in value:
                    merged[field]["description"] = value["description"]
            else:
                # New field, add to metadata
                merged[field] = value
        
        return merged
    
    def format_ssot_data(
        self, 
        entity_type: str, 
        entity_id: str, 
        job_type_id: int,
        source_platform: str,
        mapped_fields: Dict[str, Any],
        unmapped_metadata: Dict[str, Any],
        transformation_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format data in SSOT structure with mapped fields and metadata
        
        Args:
            entity_type: Type of entity (person, location, etc.)
            entity_id: ID of the entity
            job_type_id: ID of the job type
            source_platform: Source platform name
            mapped_fields: Mapped fields
            unmapped_metadata: Unmapped metadata
            transformation_info: Transformation info
            
        Returns:
            SSOT data dictionary
        """
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "job_type_id": job_type_id,
            "source_platform": source_platform,
            "mapped_fields": mapped_fields,
            "unmapped_metadata": unmapped_metadata,
            "transformation_info": transformation_info
        }
    
    def extract_entity_data(self, ssot_data: Dict[str, Any], entity_path: str) -> Dict[str, Any]:
        """
        Extract entity data from SSOT data
        
        Args:
            ssot_data: SSOT data dictionary
            entity_path: Path to the entity (e.g., "person", "location")
            
        Returns:
            Entity data dictionary
        """
        if "mapped_fields" not in ssot_data:
            logger.warning("No mapped_fields found in SSOT data")
            return {}
        
        mapped_fields = ssot_data["mapped_fields"]
        entity_data = {}
        
        # Extract all fields that start with the entity path
        prefix = f"{entity_path}."
        for field, value in mapped_fields.items():
            if field.startswith(prefix):
                # Remove the prefix and store the field
                entity_field = field[len(prefix):]
                entity_data[entity_field] = value
        
        return entity_data