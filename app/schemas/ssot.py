from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime


class PhoneNumber(BaseModel):
    """Phone number model"""
    number: str
    type: Optional[str] = None


class Address(BaseModel):
    """Address model"""
    street: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class SSOTPerson(BaseModel):
    """SSOT Person entity model"""
    id: str
    email: str
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    extension: Optional[str] = None
    phone_numbers: Optional[List[PhoneNumber]] = None
    department: Optional[str] = None


class SSOTLocation(BaseModel):
    """SSOT Location entity model"""
    id: str
    name: str
    address: Optional[Address] = None
    timezone: Optional[str] = None
    country: Optional[str] = None


class SSOTCallGroup(BaseModel):
    """SSOT Call Group entity model"""
    id: str
    name: str
    extension: Optional[str] = None
    phone_numbers: Optional[List[PhoneNumber]] = None
    members: Optional[List[str]] = None
    location_id: Optional[str] = None


class SSOTAutoAttendant(BaseModel):
    """SSOT Auto Attendant entity model"""
    id: str
    name: str
    extension: Optional[str] = None
    phone_numbers: Optional[List[PhoneNumber]] = None
    greeting: Optional[str] = None
    menu_options: Optional[Dict[str, Any]] = None
    location_id: Optional[str] = None


class ValidationResult(BaseModel):
    """Validation result model"""
    status: str
    warnings: List[str] = []
    errors: List[str] = []


class TransformationInfo(BaseModel):
    """Transformation information model"""
    field_mapping_version: str
    transformation_timestamp: str
    applied_rules: List[str] = []
    validation_results: ValidationResult


class MetadataField(BaseModel):
    """Metadata field model"""
    value: Any
    description: Optional[str] = None


class SSOTData(BaseModel):
    """SSOT data model"""
    entity_type: str
    entity_id: str
    job_type_id: int
    source_platform: str
    mapped_fields: Dict[str, Any]
    unmapped_metadata: Dict[str, MetadataField]
    transformation_info: TransformationInfo