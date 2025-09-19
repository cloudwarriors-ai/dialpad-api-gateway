from typing import Dict, List, Tuple, Any, Optional
import logging
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.models import SSOTFieldMapping, TransformationRule
from app.core.exceptions import FieldMappingError

# Configure logging
logger = logging.getLogger(__name__)


class FieldMappingService:
    """
    Service for applying field mappings and transformations
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_mappings_for_job_type(self, job_type_id: int) -> List[SSOTFieldMapping]:
        """
        Load field mappings for specific job type
        
        Args:
            job_type_id: ID of the job type
            
        Returns:
            List of field mappings for the job type
        """
        return self.db.query(SSOTFieldMapping).filter(
            SSOTFieldMapping.job_type_id == job_type_id
        ).all()
    
    def apply_field_mappings(self, source_data: Dict[str, Any], mappings: List[SSOTFieldMapping]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Apply mappings and return (mapped_data, unmapped_metadata)
        
        Args:
            source_data: Source data to map
            mappings: List of field mappings to apply
            
        Returns:
            Tuple of (mapped_data, unmapped_metadata)
        """
        mapped_data = {}
        unmapped_metadata = {}
        applied_rules = []
        validation_warnings = []
        validation_errors = []
        
        # Apply direct mappings
        for mapping in mappings:
            try:
                if mapping.source_field in source_data:
                    value = source_data[mapping.source_field]
                    
                    # Apply transformation rule if specified
                    if mapping.transformation_rule:
                        value = self._apply_transformation_rule(value, mapping.transformation_rule)
                        applied_rules.append(mapping.transformation_rule)
                    
                    # Set in target structure
                    self._set_nested_field(mapped_data, mapping.ssot_field, value)
                elif mapping.is_required:
                    # Required field is missing
                    validation_errors.append(f"Required field '{mapping.source_field}' is missing")
                    logger.warning(f"Required field '{mapping.source_field}' is missing from source data")
            except Exception as e:
                logger.error(f"Error mapping field {mapping.source_field} to {mapping.ssot_field}: {str(e)}")
                validation_errors.append(f"Error mapping field {mapping.source_field}: {str(e)}")
        
        # Collect unmapped fields for metadata
        mapped_source_fields = {m.source_field for m in mappings}
        for field, value in source_data.items():
            if field not in mapped_source_fields:
                unmapped_metadata[field] = {
                    "value": value,
                    "description": f"Unmapped Dialpad field"
                }
        
        # Generate transformation info
        transformation_info = {
            "field_mapping_version": f"dialpad_v1.0",
            "transformation_timestamp": datetime.utcnow().isoformat(),
            "applied_rules": list(set(applied_rules)),
            "validation_results": {
                "status": "valid" if not validation_errors else "invalid",
                "warnings": validation_warnings,
                "errors": validation_errors
            }
        }
        
        return mapped_data, unmapped_metadata, transformation_info
    
    def _apply_transformation_rule(self, value: Any, rule_name: str) -> Any:
        """
        Apply a transformation rule to a value
        
        Args:
            value: Value to transform
            rule_name: Name of the transformation rule
            
        Returns:
            Transformed value
        """
        # Get rule from database
        rule = self.db.query(TransformationRule).filter(
            TransformationRule.rule_name == rule_name
        ).first()
        
        if not rule:
            logger.warning(f"Transformation rule '{rule_name}' not found")
            return value
        
        # Import and call the transformation function
        try:
            from app.services.transformation_functions import get_transformation_function
            transform_func = get_transformation_function(rule.rule_function)
            
            if transform_func:
                return transform_func(value, rule.parameters)
            else:
                logger.warning(f"Transformation function '{rule.rule_function}' not found")
                return value
        except Exception as e:
            logger.error(f"Error applying transformation rule '{rule_name}': {str(e)}")
            return value
    
    def _set_nested_field(self, data: Dict[str, Any], field_path: str, value: Any):
        """
        Set a value in a nested dictionary structure
        
        Args:
            data: Dictionary to modify
            field_path: Dot-notation path to the field (e.g., "person.first_name")
            value: Value to set
        """
        parts = field_path.split('.')
        current = data
        
        # Navigate to the nested location
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the final value
        current[parts[-1]] = value