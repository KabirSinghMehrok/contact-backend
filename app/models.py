"""Pydantic models for request and response schemas."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class RequestData(BaseModel):
    """Request data containing table data."""
    table_data: List[Dict[str, Any]] = Field(..., description="List of table data items")


class ProcessRequest(BaseModel):
    """Main request model."""
    user_prompt: str = Field(..., description="User's request prompt", min_length=1, max_length=1000)
    request_data: RequestData = Field(..., description="Table data to process")


class ResponseData(BaseModel):
    """Response data containing processed table data."""
    table_data: List[Dict[str, Any]] = Field(..., description="Processed table data items")


class ProcessResponse(BaseModel):
    """Main response model."""
    ai_message: str = Field(..., description="AI's response message")
    response_data: ResponseData = Field(..., description="Processed table data")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: str = Field(..., description="Detailed error information")
