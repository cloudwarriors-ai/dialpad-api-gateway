from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime


class DialpadPhoneNumber(BaseModel):
    """Dialpad phone number model"""
    number: str
    type: Optional[str] = None


class DialpadAddress(BaseModel):
    """Dialpad address model"""
    street: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class DialpadUser(BaseModel):
    """Dialpad user model"""
    id: str
    email: str
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    extension: Optional[str] = None
    phone_numbers: Optional[List[DialpadPhoneNumber]] = None
    department: Optional[str] = None
    license_type: Optional[str] = None
    call_recording_enabled: Optional[bool] = None
    integration_settings: Optional[Dict[str, Any]] = None


class DialpadSite(BaseModel):
    """Dialpad site model"""
    office_id: str
    office_name: str
    address: Optional[DialpadAddress] = None
    timezone: Optional[str] = None
    country: Optional[str] = None
    main_number: Optional[str] = None
    office_code: Optional[str] = None


class DialpadCallQueue(BaseModel):
    """Dialpad call queue model"""
    queue_id: str
    queue_name: str
    extension: Optional[str] = None
    phone_numbers: Optional[List[DialpadPhoneNumber]] = None
    members: Optional[List[str]] = None
    office_id: Optional[str] = None
    queue_type: Optional[str] = None
    queue_settings: Optional[Dict[str, Any]] = None


class DialpadAutoReceptionist(BaseModel):
    """Dialpad auto receptionist model"""
    ivr_id: str
    ivr_name: str
    extension: Optional[str] = None
    phone_numbers: Optional[List[DialpadPhoneNumber]] = None
    greeting: Optional[str] = None
    menu_options: Optional[Dict[str, Any]] = None
    office_id: Optional[str] = None
    business_hours: Optional[Dict[str, Any]] = None