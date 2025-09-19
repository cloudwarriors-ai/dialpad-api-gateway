"""
Migration script to create SSOT field mappings for Dialpad.

This script creates the initial field mappings for Dialpad to SSOT transformations.
Run this script after the database has been initialized to populate the field mappings.
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.database.models import SSOTFieldMapping, TransformationRule
from app.database.session import get_db_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_transformation_rules():
    """Create transformation rules in the database."""
    rules = [
        {
            "rule_name": "validate_email",
            "rule_function": "validate_email",
            "description": "Validates that a value is a valid email address",
            "parameters": None
        },
        {
            "rule_name": "normalize_phone",
            "rule_function": "normalize_phone",
            "description": "Normalizes phone numbers to E.164 format",
            "parameters": None
        },
        {
            "rule_name": "normalize_phone_array",
            "rule_function": "normalize_phone_array",
            "description": "Normalizes an array of phone numbers to E.164 format",
            "parameters": None
        },
        {
            "rule_name": "generate_if_missing",
            "rule_function": "generate_if_missing",
            "description": "Generates a value if the source field is missing",
            "parameters": None
        },
        {
            "rule_name": "normalize_address",
            "rule_function": "normalize_address",
            "description": "Normalizes address fields to a standard format",
            "parameters": None
        },
        {
            "rule_name": "convert_to_iana",
            "rule_function": "convert_to_iana",
            "description": "Converts timezone strings to IANA timezone format",
            "parameters": None
        }
    ]
    
    created_rules = []
    
    with get_db_context() as db:
        for rule_data in rules:
            rule = TransformationRule(**rule_data)
            db.add(rule)
            created_rules.append(rule)
        
        db.commit()
        logger.info(f"Created {len(created_rules)} transformation rules")
    
    return created_rules


def create_users_field_mappings():
    """Create field mappings for Dialpad Users -> SSOT Person (JobType 60)."""
    mappings = [
        # Dialpad User to SSOT Person mappings (JobType 60)
        {
            "job_type_id": 60,
            "source_platform": "dialpad",
            "target_entity": "person",
            "ssot_field": "person.id",
            "source_field": "id",
            "transformation_rule": None,
            "is_required": True,
            "description": "Unique identifier for the person"
        },
        {
            "job_type_id": 60,
            "source_platform": "dialpad",
            "target_entity": "person",
            "ssot_field": "person.email",
            "source_field": "email",
            "transformation_rule": "validate_email",
            "is_required": True,
            "description": "Primary email address for the person"
        },
        {
            "job_type_id": 60,
            "source_platform": "dialpad",
            "target_entity": "person",
            "ssot_field": "person.first_name",
            "source_field": "first_name",
            "transformation_rule": None,
            "is_required": True,
            "description": "First name of the person"
        },
        {
            "job_type_id": 60,
            "source_platform": "dialpad",
            "target_entity": "person",
            "ssot_field": "person.last_name",
            "source_field": "last_name",
            "transformation_rule": None,
            "is_required": True,
            "description": "Last name of the person"
        },
        {
            "job_type_id": 60,
            "source_platform": "dialpad",
            "target_entity": "person",
            "ssot_field": "person.display_name",
            "source_field": "display_name",
            "transformation_rule": "generate_if_missing",
            "is_required": False,
            "description": "Display name for the person"
        },
        {
            "job_type_id": 60,
            "source_platform": "dialpad",
            "target_entity": "person",
            "ssot_field": "person.extension",
            "source_field": "extension",
            "transformation_rule": None,
            "is_required": False,
            "description": "Extension number for the person"
        },
        {
            "job_type_id": 60,
            "source_platform": "dialpad",
            "target_entity": "person",
            "ssot_field": "person.phone_numbers",
            "source_field": "phone_numbers",
            "transformation_rule": "normalize_phone_array",
            "is_required": False,
            "description": "Phone numbers associated with the person"
        },
        {
            "job_type_id": 60,
            "source_platform": "dialpad",
            "target_entity": "person",
            "ssot_field": "person.department",
            "source_field": "department",
            "transformation_rule": None,
            "is_required": False,
            "description": "Department the person belongs to"
        }
    ]
    
    with get_db_context() as db:
        for mapping_data in mappings:
            mapping = SSOTFieldMapping(**mapping_data)
            db.add(mapping)
        
        db.commit()
        logger.info(f"Created {len(mappings)} field mappings for Dialpad Users -> SSOT Person (JobType 60)")


def create_sites_field_mappings():
    """Create field mappings for Dialpad Sites -> SSOT Location (JobType 61)."""
    mappings = [
        # Dialpad Sites to SSOT Location mappings (JobType 61)
        {
            "job_type_id": 61,
            "source_platform": "dialpad",
            "target_entity": "location",
            "ssot_field": "location.id",
            "source_field": "office_id",
            "transformation_rule": None,
            "is_required": True,
            "description": "Unique identifier for the location"
        },
        {
            "job_type_id": 61,
            "source_platform": "dialpad",
            "target_entity": "location",
            "ssot_field": "location.name",
            "source_field": "office_name",
            "transformation_rule": None,
            "is_required": True,
            "description": "Name of the location"
        },
        {
            "job_type_id": 61,
            "source_platform": "dialpad",
            "target_entity": "location",
            "ssot_field": "location.address",
            "source_field": "address",
            "transformation_rule": "normalize_address",
            "is_required": False,
            "description": "Physical address of the location"
        },
        {
            "job_type_id": 61,
            "source_platform": "dialpad",
            "target_entity": "location",
            "ssot_field": "location.timezone",
            "source_field": "timezone",
            "transformation_rule": "convert_to_iana",
            "is_required": False,
            "description": "Timezone for the location"
        },
        {
            "job_type_id": 61,
            "source_platform": "dialpad",
            "target_entity": "location",
            "ssot_field": "location.country",
            "source_field": "country",
            "transformation_rule": None,
            "is_required": False,
            "description": "Country where the location is situated"
        }
    ]
    
    with get_db_context() as db:
        for mapping_data in mappings:
            mapping = SSOTFieldMapping(**mapping_data)
            db.add(mapping)
        
        db.commit()
        logger.info(f"Created {len(mappings)} field mappings for Dialpad Sites -> SSOT Location (JobType 61)")


def create_call_queues_field_mappings():
    """Create field mappings for Dialpad Call Queues -> SSOT CallGroup (JobType 62)."""
    mappings = [
        # Dialpad Call Queues to SSOT CallGroup mappings (JobType 62)
        {
            "job_type_id": 62,
            "source_platform": "dialpad",
            "target_entity": "call_group",
            "ssot_field": "call_group.id",
            "source_field": "queue_id",
            "transformation_rule": None,
            "is_required": True,
            "description": "Unique identifier for the call queue"
        },
        {
            "job_type_id": 62,
            "source_platform": "dialpad",
            "target_entity": "call_group",
            "ssot_field": "call_group.name",
            "source_field": "queue_name",
            "transformation_rule": None,
            "is_required": True,
            "description": "Name of the call queue"
        },
        {
            "job_type_id": 62,
            "source_platform": "dialpad",
            "target_entity": "call_group",
            "ssot_field": "call_group.extension",
            "source_field": "extension",
            "transformation_rule": None,
            "is_required": False,
            "description": "Extension number for the call queue"
        },
        {
            "job_type_id": 62,
            "source_platform": "dialpad",
            "target_entity": "call_group",
            "ssot_field": "call_group.phone_numbers",
            "source_field": "phone_numbers",
            "transformation_rule": "normalize_phone_array",
            "is_required": False,
            "description": "Phone numbers associated with the call queue"
        },
        {
            "job_type_id": 62,
            "source_platform": "dialpad",
            "target_entity": "call_group",
            "ssot_field": "call_group.members",
            "source_field": "members",
            "transformation_rule": None,
            "is_required": False,
            "description": "Members assigned to the call queue"
        },
        {
            "job_type_id": 62,
            "source_platform": "dialpad",
            "target_entity": "call_group",
            "ssot_field": "call_group.location_id",
            "source_field": "office_id",
            "transformation_rule": None,
            "is_required": False,
            "description": "Location ID where the call queue is assigned"
        }
    ]
    
    with get_db_context() as db:
        for mapping_data in mappings:
            mapping = SSOTFieldMapping(**mapping_data)
            db.add(mapping)
        
        db.commit()
        logger.info(f"Created {len(mappings)} field mappings for Dialpad Call Queues -> SSOT CallGroup (JobType 62)")


def create_auto_receptionists_field_mappings():
    """Create field mappings for Dialpad Auto Receptionists -> SSOT AutoAttendant (JobType 63)."""
    mappings = [
        # Dialpad Auto Receptionists to SSOT AutoAttendant mappings (JobType 63)
        {
            "job_type_id": 63,
            "source_platform": "dialpad",
            "target_entity": "auto_attendant",
            "ssot_field": "auto_attendant.id",
            "source_field": "ivr_id",
            "transformation_rule": None,
            "is_required": True,
            "description": "Unique identifier for the auto receptionist"
        },
        {
            "job_type_id": 63,
            "source_platform": "dialpad",
            "target_entity": "auto_attendant",
            "ssot_field": "auto_attendant.name",
            "source_field": "ivr_name",
            "transformation_rule": None,
            "is_required": True,
            "description": "Name of the auto receptionist"
        },
        {
            "job_type_id": 63,
            "source_platform": "dialpad",
            "target_entity": "auto_attendant",
            "ssot_field": "auto_attendant.extension",
            "source_field": "extension",
            "transformation_rule": None,
            "is_required": False,
            "description": "Extension number for the auto receptionist"
        },
        {
            "job_type_id": 63,
            "source_platform": "dialpad",
            "target_entity": "auto_attendant",
            "ssot_field": "auto_attendant.phone_numbers",
            "source_field": "phone_numbers",
            "transformation_rule": "normalize_phone_array",
            "is_required": False,
            "description": "Phone numbers associated with the auto receptionist"
        },
        {
            "job_type_id": 63,
            "source_platform": "dialpad",
            "target_entity": "auto_attendant",
            "ssot_field": "auto_attendant.greeting",
            "source_field": "greeting",
            "transformation_rule": None,
            "is_required": False,
            "description": "Greeting message for the auto receptionist"
        },
        {
            "job_type_id": 63,
            "source_platform": "dialpad",
            "target_entity": "auto_attendant",
            "ssot_field": "auto_attendant.menu_options",
            "source_field": "menu_options",
            "transformation_rule": None,
            "is_required": False,
            "description": "Menu options for the auto receptionist"
        },
        {
            "job_type_id": 63,
            "source_platform": "dialpad",
            "target_entity": "auto_attendant",
            "ssot_field": "auto_attendant.location_id",
            "source_field": "office_id",
            "transformation_rule": None,
            "is_required": False,
            "description": "Location ID where the auto receptionist is assigned"
        }
    ]
    
    with get_db_context() as db:
        for mapping_data in mappings:
            mapping = SSOTFieldMapping(**mapping_data)
            db.add(mapping)
        
        db.commit()
        logger.info(f"Created {len(mappings)} field mappings for Dialpad Auto Receptionists -> SSOT AutoAttendant (JobType 63)")


def run_migrations():
    """Run all migrations."""
    try:
        logger.info("Starting migrations...")
        
        # Create transformation rules
        create_transformation_rules()
        
        # Create field mappings for each job type
        create_users_field_mappings()
        create_sites_field_mappings()
        create_call_queues_field_mappings()
        create_auto_receptionists_field_mappings()
        
        logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    run_migrations()