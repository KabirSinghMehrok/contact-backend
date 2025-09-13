# LLM Backend API

A production-ready FastAPI backend for LLM-based table data processing using Google's Gemini model via LangChain.

## Features

- **Intent Classification**: Automatically classifies user requests into predefined categories
- **Data Processing**: Processes table data based on classified intent
- **API Key Authentication**: Simple API key-based authentication
- **Rate Limiting**: Basic rate limiting to prevent abuse
- **Docker Support**: Ready for containerized deployment
- **Health Checks**: Built-in health monitoring
- **Structured Logging**: Comprehensive logging for debugging and monitoring

## Quick Start

### 1. Environment Setup

```bash
# Clone and navigate to the project
cd contact-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
# At minimum, set:
# - GOOGLE_API_KEY=your_google_api_key_here
# - SECRET_KEY=your_secret_key_here
```

### 3. Run the Application

```bash
# Development
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Process data (replace YOUR_API_KEY with actual key)
curl -X POST "http://localhost:8000/api/v1/process" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "user_prompt": "Filter products with price > 100",
    "request_data": {
      "table_data": [
        {"data": {"name": "Product A", "price": 150, "category": "Electronics"}},
        {"data": {"name": "Product B", "price": 50, "category": "Books"}}
      ]
    }
  }'
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI API key | Required |
| `SECRET_KEY` | Secret key for security | Change in production |
| `API_KEY_HEADER` | Header name for API key | `X-API-Key` |
| `RATE_LIMIT_PER_MINUTE` | Rate limit per API key | `100` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEBUG` | Debug mode | `False` |

### Intent Categories

Modify `config.py` to change the intent categories:

```python
INTENT_CATEGORIES = [
    "data_filtering",      # Filter, search, select data
    "data_transformation", # Modify, format, restructure data
    "data_analysis"        # Analyze, summarize, generate insights
]
```

## Request/Response Format

### Request
```json
{
  "user_prompt": "User request here",
  "request_data": {
    "table_data": [
      {"data": {"key": "value", "another_key": "another_value"}},
      {"data": {"key": "value2", "another_key": "another_value2"}}
    ]
  }
}
```

### Response
```json
{
  "ai_message": "AI response message",
  "response_data": {
    "table_data": [
      {"data": {"key": "processed_value", "another_key": "processed_value"}},
      {"data": {"key": "processed_value2", "another_key": "processed_value2"}}
    ]
  }
}
```

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t llm-backend .

# Run container
docker run -p 8000:8000 --env-file .env llm-backend
```

### Docker Compose (Optional)

```yaml
version: '3.8'
services:
  llm-backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
```

## Deployment on Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in Render dashboard
6. Deploy!

## Project Structure

```
contact-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── llm_service.py       # LLM integration
│   ├── security.py          # Authentication & rate limiting
│   └── routers/
│       ├── __init__.py
│       └── process.py       # Processing endpoints
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── .dockerignore           # Docker ignore file
├── env.example             # Environment template
└── README.md               # This file
```

## Development

### Adding New Intent Categories

1. Update `INTENT_CATEGORIES` in `config.py`
2. Add corresponding processing function in `LLMService`
3. Update the `process_data` method to handle the new intent

### Adding New Endpoints

1. Create new router in `app/routers/`
2. Include router in `app/main.py`
3. Follow the same authentication pattern

## Security Notes

- Change `SECRET_KEY` in production
- Configure proper CORS origins
- Consider implementing proper API key validation
- Monitor rate limiting effectiveness
- Use HTTPS in production

## Troubleshooting

### Common Issues

1. **Google API Key Error**: Ensure `GOOGLE_API_KEY` is set correctly
2. **Import Errors**: Make sure all dependencies are installed
3. **Rate Limit**: Check if you're hitting the rate limit
4. **CORS Issues**: Configure CORS middleware for your frontend domain

### Logs

Check application logs for detailed error information:
```bash
# If running with uvicorn
uvicorn app.main:app --log-level debug
```
