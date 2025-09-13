# Low-Level Design (LLD) Diagram - LLM Backend API

## System Architecture Overview

This is a FastAPI-based backend service that processes table data using Google's Gemini AI through LangChain. The system provides intelligent data transformation capabilities with API key authentication and rate limiting.

## Mermaid Diagram

```mermaid
graph TB
    %% External Systems
    Client[Client Application]
    GoogleAI[Google Gemini AI API]
    
    %% Main Application Layer
    subgraph "FastAPI Application"
        Main[main.py<br/>FastAPI App]
        CORS[CORS Middleware]
        Router[process.py<br/>API Router]
    end
    
    %% Service Layer
    subgraph "Service Layer"
        LLMService[llm_service.py<br/>LLMService]
        Security[security.py<br/>Security Utils]
    end
    
    %% Data Models
    subgraph "Data Models"
        Models[models.py<br/>Pydantic Models]
        RequestModel[ProcessRequest]
        ResponseModel[ProcessResponse]
        ErrorModel[ErrorResponse]
    end
    
    %% Configuration
    subgraph "Configuration"
        Config[config.py<br/>Settings]
        EnvVars[Environment Variables]
    end
    
    %% Core Processing Flow
    subgraph "Processing Pipeline"
        IntentClass[Intent Classification]
        DataProcess[Data Processing]
        ResponseParse[Response Parsing]
    end
    
    %% Processing Functions
    subgraph "LLM Processing Functions"
        Transform[_transform_data]
        Filter[_filter_data]
        Analyze[_analyze_data]
        Normalize[_normalize_contact_signals]
    end
    
    %% Security Components
    subgraph "Security Layer"
        APIKeyValidation[API Key Validation]
        RateLimit[Rate Limiting]
        InMemoryStorage[In-Memory Storage]
    end
    
    %% Request Flow
    Client -->|POST /api/v1/process| Main
    Main --> CORS
    CORS --> Router
    
    %% Router Processing
    Router -->|Verify API Key| Security
    Security --> APIKeyValidation
    APIKeyValidation --> RateLimit
    RateLimit --> InMemoryStorage
    
    %% Data Processing
    Router -->|Initialize| LLMService
    LLMService -->|Classify Intent| IntentClass
    IntentClass -->|Process Data| DataProcess
    
    %% LLM Processing Functions
    DataProcess --> Transform
    DataProcess --> Filter
    DataProcess --> Analyze
    Transform --> ResponseParse
    Filter --> ResponseParse
    Analyze --> ResponseParse
    
    %% Data Normalization
    ResponseParse --> Normalize
    
    %% External API Call
    LLMService -->|LangChain| GoogleAI
    
    %% Response Flow
    Router -->|Return| ResponseModel
    Router -->|Error| ErrorModel
    
    %% Configuration Dependencies
    Main --> Config
    LLMService --> Config
    Security --> Config
    Config --> EnvVars
    
    %% Model Dependencies
    Router --> Models
    Models --> RequestModel
    Models --> ResponseModel
    Models --> ErrorModel
    
    %% Styling
    classDef external fill:#e1f5fe
    classDef service fill:#f3e5f5
    classDef model fill:#e8f5e8
    classDef config fill:#fff3e0
    classDef security fill:#ffebee
    classDef process fill:#f1f8e9
    
    class Client,GoogleAI external
    class Main,Router,LLMService,Security service
    class Models,RequestModel,ResponseModel,ErrorModel model
    class Config,EnvVars config
    class APIKeyValidation,RateLimit,InMemoryStorage security
    class IntentClass,DataProcess,ResponseParse,Transform,Filter,Analyze,Normalize process
```

## Component Details

### 1. **FastAPI Application Layer**
- **main.py**: Core FastAPI application with CORS middleware
- **process.py**: API router handling `/api/v1/process` endpoint
- **CORS Middleware**: Handles cross-origin requests

### 2. **Service Layer**
- **LLMService**: Main service for AI operations using LangChain
- **Security**: API key validation and rate limiting utilities

### 3. **Data Models (Pydantic)**
- **ProcessRequest**: Input model with user prompt and table data
- **ProcessResponse**: Output model with AI message and processed data
- **ErrorResponse**: Error handling model

### 4. **Configuration Management**
- **config.py**: Centralized settings management
- Environment variables for API keys, rate limits, and logging

### 5. **Processing Pipeline**
- **Intent Classification**: Determines user intent (currently only data_transformation)
- **Data Processing**: Applies appropriate processing function
- **Response Parsing**: Extracts and validates LLM responses

### 6. **LLM Processing Functions**
- **_transform_data**: Adds new fields based on user requests
- **_filter_data**: Filters data based on criteria
- **_analyze_data**: Performs data analysis
- **_normalize_contact_signals**: Normalizes data types

### 7. **Security Layer**
- **API Key Validation**: Simple validation for MVP
- **Rate Limiting**: Per-minute request limits (default: 100/min)
- **In-Memory Storage**: Temporary storage for rate limit tracking

## Key Features

1. **AI-Powered Data Processing**: Uses Google Gemini AI for intelligent data transformation
2. **Intent Classification**: Automatically determines user intent (currently focused on data transformation)
3. **API Security**: API key authentication with rate limiting
4. **Robust Error Handling**: Comprehensive error responses and logging
5. **Docker Support**: Containerized deployment with health checks
6. **Flexible Data Processing**: Supports filtering, transformation, and analysis operations

## API Endpoints

- `POST /api/v1/process`: Main data processing endpoint
- `GET /api/v1/health`: Health check endpoint
- `GET /`: Root endpoint with API status

## External Dependencies

- **Google Gemini AI**: For LLM processing via LangChain
- **FastAPI**: Web framework
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production deployment
