"""Process router for handling data processing requests."""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.models import ProcessRequest, ProcessResponse, ErrorResponse
from app.security import verify_api_key, get_api_key_from_header
from app.llm_service import LLMService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["processing"])


@router.post(
    "/process",
    response_model=ProcessResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def process_data(
    request: ProcessRequest,
    api_key: str = Header(None, alias="X-API-Key")
) -> ProcessResponse:
    """
    Process table data based on user prompt.
    
    This endpoint:
    1. Classifies the user's intent
    2. Processes the table data accordingly
    3. Returns the AI response and processed data
    """
    try:
        # Verify API key and rate limiting
        await verify_api_key(get_api_key_from_header(api_key))
        
        logger.info(f"Processing request from user: {request.user_prompt[:50]}...")
        
        # Initialize LLM service
        llm_service = LLMService()
        
        # Convert table data to simple format for processing
        table_data = request.request_data.table_data
        
        # Classify intent
        intent = await llm_service.classify_intent(request.user_prompt)
        logger.info(f"Classified intent: {intent}")
        
        # Process data based on intent
        ai_message, processed_data = await llm_service.process_data(
            intent, request.user_prompt, table_data
        )
        
        # Return processed data directly (no wrapping needed)
        logger.info("Request processed successfully")
        
        return ProcessResponse(
            ai_message=ai_message,
            response_data={"table_data": processed_data}
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (auth, rate limit)
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while processing your request"
        )


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "LLM Backend API"}
