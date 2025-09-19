from typing import Any, Dict, List, Optional
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)


def get_transformation_function(function_name: str):
    """
    Get a transformation function by name
    
    Args:
        function_name: Name of the function to get
        
    Returns:
        Function reference or None if not found
    """
    transformation_functions = {
        "validate_email": validate_email,
        "normalize_phone": normalize_phone,
        "normalize_phone_array": normalize_phone_array,
        "generate_if_missing": generate_if_missing,
        "normalize_address": normalize_address,
        "convert_to_iana": convert_to_iana
    }
    
    return transformation_functions.get(function_name)


def validate_email(value: str, params: Optional[Dict[str, Any]] = None) -> str:
    """
    Validate that a value is a valid email address
    
    Args:
        value: Email address to validate
        params: Optional parameters
        
    Returns:
        Validated email address or original value if invalid
    """
    if not value:
        return value
    
    # Simple email validation regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, value):
        return value
    else:
        logger.warning(f"Invalid email address: {value}")
        return value  # Return original value, but could raise an exception


def normalize_phone(value: str, params: Optional[Dict[str, Any]] = None) -> str:
    """
    Normalize a phone number to E.164 format
    
    Args:
        value: Phone number to normalize
        params: Optional parameters
        
    Returns:
        Normalized phone number
    """
    if not value:
        return value
    
    # Remove non-digit characters
    digits_only = re.sub(r'\D', '', value)
    
    # Handle US numbers (default if no country code)
    if len(digits_only) == 10:
        return f"+1{digits_only}"
    elif len(digits_only) > 10 and digits_only.startswith('1'):
        return f"+{digits_only}"
    elif len(digits_only) > 10:
        return f"+{digits_only}"
    else:
        logger.warning(f"Unable to normalize phone number: {value}")
        return value


def normalize_phone_array(value: List[Dict[str, Any]], params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Normalize an array of phone numbers to E.164 format
    
    Args:
        value: Array of phone numbers to normalize
        params: Optional parameters
        
    Returns:
        Array of normalized phone numbers
    """
    if not value or not isinstance(value, list):
        return value
    
    normalized = []
    for phone in value:
        if isinstance(phone, dict) and 'number' in phone:
            phone_copy = phone.copy()
            phone_copy['number'] = normalize_phone(phone['number'])
            normalized.append(phone_copy)
        else:
            normalized.append(phone)
    
    return normalized


def generate_if_missing(value: Any, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Generate a value if the original is missing
    
    Args:
        value: Original value
        params: Optional parameters with context
        
    Returns:
        Original value or generated value if missing
    """
    if value:
        return value
    
    # If params contains first_name and last_name, generate display_name
    if params and 'context' in params:
        context = params['context']
        if 'first_name' in context and 'last_name' in context:
            return f"{context['first_name']} {context['last_name']}"
    
    return value


def normalize_address(value: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Normalize address fields to a standard format
    
    Args:
        value: Address to normalize
        params: Optional parameters
        
    Returns:
        Normalized address
    """
    if not value or not isinstance(value, dict):
        return value
    
    # Create a standardized address format
    normalized = {}
    
    # Map common field variations to standard names
    field_mapping = {
        'street': ['street', 'street_address', 'address_line_1', 'line1'],
        'street2': ['street2', 'address_line_2', 'line2'],
        'city': ['city', 'locality'],
        'state': ['state', 'region', 'province'],
        'postal_code': ['postal_code', 'zip', 'zip_code', 'postcode'],
        'country': ['country', 'country_code']
    }
    
    # Normalize fields based on mapping
    for standard_field, field_variations in field_mapping.items():
        for field in field_variations:
            if field in value:
                normalized[standard_field] = value[field]
                break
    
    # Copy any additional fields not in our mapping
    for field, field_value in value.items():
        if not any(field in variations for variations in field_mapping.values()):
            normalized[field] = field_value
    
    return normalized


def convert_to_iana(value: str, params: Optional[Dict[str, Any]] = None) -> str:
    """
    Convert timezone strings to IANA timezone format
    
    Args:
        value: Timezone to convert
        params: Optional parameters
        
    Returns:
        IANA timezone
    """
    if not value:
        return value
    
    # Common timezone mappings (partial list)
    timezone_mapping = {
        'EST': 'America/New_York',
        'EDT': 'America/New_York',
        'CST': 'America/Chicago',
        'CDT': 'America/Chicago',
        'MST': 'America/Denver',
        'MDT': 'America/Denver',
        'PST': 'America/Los_Angeles',
        'PDT': 'America/Los_Angeles',
        'GMT': 'Europe/London',
        'UTC': 'UTC',
    }
    
    # Return mapped value if found, otherwise return original
    return timezone_mapping.get(value.upper(), value)