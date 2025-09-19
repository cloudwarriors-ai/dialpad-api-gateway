from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class SSOTFieldMapping(Base):
    """
    Stores field mappings between source platforms and SSOT schema
    """
    __tablename__ = "ssot_field_mappings"
    
    id = Column(Integer, primary_key=True)
    job_type_id = Column(Integer, nullable=False, index=True)
    source_platform = Column(String(50), nullable=False)  
    target_entity = Column(String(50), nullable=False)    
    ssot_field = Column(String(100), nullable=False)      
    source_field = Column(String(100), nullable=False)    
    transformation_rule = Column(String(200))             
    is_required = Column(Boolean, default=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class TransformationRule(Base):
    """
    Stores transformation rules to be applied during field mapping
    """
    __tablename__ = "transformation_rules"
    
    id = Column(Integer, primary_key=True)
    rule_name = Column(String(50), unique=True, nullable=False)
    rule_function = Column(String(100), nullable=False)  # Python function name
    description = Column(Text)
    parameters = Column(JSON)  # Rule-specific parameters


class DialpadCredential(Base):
    """
    Stores Dialpad API credentials for authentication
    """
    __tablename__ = "dialpad_credentials"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(255), unique=True, index=True)
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_type = Column(String(50), default="bearer")
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    extract_jobs = relationship("ExtractJob", back_populates="credential")


class ExtractJob(Base):
    """
    Tracks data extraction jobs from Dialpad API
    """
    __tablename__ = "extract_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(255), unique=True, index=True)
    credential_id = Column(Integer, ForeignKey("dialpad_credentials.id"))
    resource_type = Column(String(100))  # users, sites, call_queues, etc.
    parameters = Column(JSON)  # Query parameters used for extraction
    status = Column(String(50))  # pending, in_progress, completed, failed
    result_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    credential = relationship("DialpadCredential", back_populates="extract_jobs")
    extracted_data = relationship("ExtractedData", back_populates="extract_job")


class ExtractedData(Base):
    """
    Stores data extracted from Dialpad API
    """
    __tablename__ = "extracted_data"

    id = Column(Integer, primary_key=True, index=True)
    extract_job_id = Column(Integer, ForeignKey("extract_jobs.id"))
    resource_id = Column(String(255), index=True)  # Dialpad resource ID
    resource_type = Column(String(100))  # users, sites, call_queues, etc.
    data = Column(JSON)  # Raw JSON data from Dialpad API
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    extract_job = relationship("ExtractJob", back_populates="extracted_data")


class MCPRequest(Base):
    """
    Tracks Machine Communication Protocol requests
    """
    __tablename__ = "mcp_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(255), unique=True, index=True)
    operation = Column(String(100))  # extract, transform, load, etc.
    parameters = Column(JSON)
    status = Column(String(50))  # pending, in_progress, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    responses = relationship("MCPResponse", back_populates="request")


class MCPResponse(Base):
    """
    Stores responses to MCP requests
    """
    __tablename__ = "mcp_responses"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("mcp_requests.id"))
    status_code = Column(Integer)
    content = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    request = relationship("MCPRequest", back_populates="responses")


class TransformedSSOTData(Base):
    """
    Stores SSOT-transformed data for auditing and debugging
    """
    __tablename__ = "transformed_ssot_data"
    
    id = Column(Integer, primary_key=True)
    job_type_id = Column(Integer, nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # person, location, etc.
    entity_id = Column(String(255), nullable=False, index=True)
    source_platform = Column(String(50), nullable=False)
    source_data_id = Column(String(255), nullable=True)  # Original source data ID
    mapped_fields = Column(JSON, nullable=False)  # SSOT field-mapped data
    unmapped_metadata = Column(JSON, nullable=False)  # Unmapped source fields
    transformation_info = Column(JSON, nullable=False)  # Transformation metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    

class JobTypeConfig(Base):
    """
    Represents a type of ETL job that can be performed
    """
    __tablename__ = "job_type_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    code = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    source_platform_id = Column(Integer, nullable=True)
    target_platform_id = Column(Integer, nullable=True)
    prompt = Column(Text, nullable=True)
    is_extraction_only = Column(Boolean, default=False)
    jobtype_dependencies = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)