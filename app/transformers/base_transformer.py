from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional


class BaseTransformer(ABC):
    """
    Abstract base class for all data transformers.
    
    This class defines the interface for transformers that convert data
    between different formats and systems. Subclasses must implement
    the transform method.
    """
    
    def __init__(self):
        """Initialize the transformer with a logger."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.transformation_config = None
        self.job_type_code = None
        self.source_format = None
        self.target_format = None
    
    def get_transformation_config(self, config_id: str) -> Dict[str, Any]:
        """
        Retrieve transformation configuration.
        
        Args:
            config_id: Configuration identifier
            
        Returns:
            Dictionary containing transformation mapping rules and settings
        """
        # For now, return empty config - can be enhanced with database lookup later
        return {}
    
    def convert_country_to_iso(self, country_name: str) -> str:
        """
        Convert country name to ISO 3166-1 alpha-2 code.
        
        Args:
            country_name: Country name to convert
            
        Returns:
            ISO country code
        """
        # Country name to ISO code mapping
        country_mapping = {
            'United States': 'US',
            'United States of America': 'US', 
            'USA': 'US',
            'US': 'US',
            'us': 'US',
            'Canada': 'CA',
            'United Kingdom': 'GB',
            'Great Britain': 'GB',
            'UK': 'GB',
            'Australia': 'AU',
            'Germany': 'DE',
            'France': 'FR',
            'Japan': 'JP',
            'China': 'CN',
            'India': 'IN',
            'Brazil': 'BR',
            'Mexico': 'MX'
        }
        
        return country_mapping.get(country_name, country_name.upper())
    
    @abstractmethod
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform the input data to the target format.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Transformed data dictionary
        """
        pass