from typing import Dict, Any, List, Optional
import logging
import json
from sqlalchemy.orm import Session

from app.database.models import JobTypeConfig

# Configure logging
logger = logging.getLogger(__name__)


class ConfigService:
    """
    Service for handling transformation configurations
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_job_type_config(self, job_type_id: int) -> Optional[JobTypeConfig]:
        """
        Get job type configuration by ID
        
        Args:
            job_type_id: Job type ID
            
        Returns:
            JobTypeConfig if found, None otherwise
        """
        return self.db.query(JobTypeConfig).filter(
            JobTypeConfig.id == job_type_id
        ).first()
    
    def get_job_type_by_code(self, code: str) -> Optional[JobTypeConfig]:
        """
        Get job type configuration by code
        
        Args:
            code: Job type code
            
        Returns:
            JobTypeConfig if found, None otherwise
        """
        return self.db.query(JobTypeConfig).filter(
            JobTypeConfig.code == code
        ).first()
    
    def get_job_types_for_platforms(self, source_platform_id: int, target_platform_id: int) -> List[JobTypeConfig]:
        """
        Get job types for specific source and target platforms
        
        Args:
            source_platform_id: Source platform ID
            target_platform_id: Target platform ID
            
        Returns:
            List of JobTypeConfig
        """
        return self.db.query(JobTypeConfig).filter(
            JobTypeConfig.source_platform_id == source_platform_id,
            JobTypeConfig.target_platform_id == target_platform_id
        ).all()
    
    def get_transformation_config(self, job_type_id: int, target_entity: str) -> Dict[str, Any]:
        """
        Get transformation configuration for job type and target entity
        
        Args:
            job_type_id: Job type ID
            target_entity: Target entity name
            
        Returns:
            Transformation configuration dictionary
        """
        # For now, return a simple configuration based on the target entity
        # In a real implementation, this would be retrieved from a database or configuration file
        
        if target_entity == "person":
            return {
                "entity_type": "person",
                "required_fields": ["id", "email", "first_name", "last_name"],
                "optional_fields": ["display_name", "extension", "phone_numbers", "department"],
                "transformation_rules": {
                    "email": "validate_email",
                    "phone_numbers": "normalize_phone_array",
                    "display_name": "generate_if_missing"
                }
            }
        elif target_entity == "location":
            return {
                "entity_type": "location",
                "required_fields": ["id", "name"],
                "optional_fields": ["address", "timezone", "country"],
                "transformation_rules": {
                    "address": "normalize_address",
                    "timezone": "convert_to_iana"
                }
            }
        elif target_entity == "call_group":
            return {
                "entity_type": "call_group",
                "required_fields": ["id", "name"],
                "optional_fields": ["extension", "phone_numbers", "members", "location_id"],
                "transformation_rules": {
                    "phone_numbers": "normalize_phone_array"
                }
            }
        elif target_entity == "auto_attendant":
            return {
                "entity_type": "auto_attendant",
                "required_fields": ["id", "name"],
                "optional_fields": ["extension", "phone_numbers", "greeting", "menu_options", "location_id"],
                "transformation_rules": {
                    "phone_numbers": "normalize_phone_array"
                }
            }
        else:
            # Default empty configuration
            return {
                "entity_type": target_entity,
                "required_fields": [],
                "optional_fields": [],
                "transformation_rules": {}
            }