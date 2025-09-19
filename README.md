# Dialpad Platform Microservice

## Overview

This microservice is part of the CloudWarriors ETL system, focused specifically on integrating with the Dialpad API and implementing SSOT field mapping. It provides a standardized interface for transforming Dialpad data to SSOT format.

## Purpose

The Dialpad Platform Microservice serves as a dedicated connector between the CloudWarriors ETL system and Dialpad's API services. Its primary responsibilities include:

- **Field Mapping**: Implementing field mappings between Dialpad and SSOT schemas
- **Metadata Handling**: Managing unmapped fields through metadata
- **SSOT Transformation**: Converting Dialpad data to the system's standardized SSOT schema
- **MCP Protocol Support**: Implementing Machine Communication Protocol for AI-assisted operations

## Architecture

This service follows a modular, field-mapping based architecture:

- `app/core`: Core configuration and shared utilities
- `app/database`: Database models and connection management, including SSOT field mappings
- `app/services`: Field mapping, metadata, and configuration services
- `app/transformers`: Dialpad → SSOT transformers for various entity types
- `app/routers`: API route definitions and endpoint handlers
- `app/schemas`: Pydantic models for request/response validation

## Getting Started

### Prerequisites

- Python 3.9+
- FastAPI
- SQLAlchemy
- PostgreSQL

### Installation

```bash
# Clone the repository
git clone https://github.com/cloudwarriors/dialpad-platform-microservice.git
cd dialpad-platform-microservice

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app.main:app --reload
```

### Docker Setup

```bash
# Build and start the microservice
docker-compose up -d

# Verify the microservice is running
curl http://localhost:3556/health

# Apply database migrations
docker-compose exec microservice python -m app.database.migrations.create_ssot_mappings
```

## API Documentation

When the service is running, visit:
- Swagger UI: http://localhost:3556/docs
- ReDoc: http://localhost:3556/redoc

## Field Mapping System

The core feature of this microservice is its field mapping system:

### SSOT Field Mappings

The microservice implements a field mapping approach that maps Dialpad fields to SSOT fields:

```
Dialpad Field → SSOT Field (with optional transformation)
```

For example:
- `email` → `person.email` (with validation)
- `first_name` → `person.first_name`
- `phone_numbers` → `person.phone_numbers` (with normalization)

### Unmapped Field Handling

Fields that don't have explicit mappings are preserved as metadata:

```json
"unmapped_metadata": {
  "dialpad_license_type": {
    "value": "premium",
    "description": "Dialpad-specific license level"
  }
}
```

### Supported Job Types

The microservice supports the following job types:

- **JobType 60**: Dialpad Users → SSOT Person
- **JobType 61**: Dialpad Sites → SSOT Location
- **JobType 62**: Dialpad Call Queues → SSOT CallGroup
- **JobType 63**: Dialpad Auto Receptionists → SSOT AutoAttendant

## Integration with Main ETL System

This microservice integrates with the main ETL system via MCP protocol:

```
Dialpad Extractor → Dialpad Microservice → SSOT Format → Main ETL Storage → Zoom Microservice → Zoom Format → Loader
```

### Network Configuration

The microservice runs on port `3556` and connects to:

- **Microservice URL**: `http://localhost:3556`
- **From ETL System**: `http://host.docker.internal:3556`
- **Database**: PostgreSQL on port `5434` (separate from main ETL system)

## License

Copyright © 2023 CloudWarriors. All rights reserved.