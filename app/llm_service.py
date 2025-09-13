"""LLM service for intent classification and data processing using LangChain."""

import logging
from typing import List, Dict, Any, Literal, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings
from pydantic import BaseModel, Field
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM operations."""
    
    def __init__(self):
        """Initialize LLM service."""
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.1
        )
    
    async def classify_intent(self, user_prompt: str) -> str:
        """Classify user intent into predefined categories."""
        try:
            system_prompt = f"""
            You are an intent classification system. Classify the user's request into one of these categories:
            {', '.join(settings.INTENT_CATEGORIES)}
            
            Return only the category name, nothing else.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            intent = response.content.strip().lower()
            
            # Validate intent is in our categories
            if intent not in settings.INTENT_CATEGORIES:
                logger.warning(f"Invalid intent '{intent}' for prompt: {user_prompt}")
                return settings.INTENT_CATEGORIES[0]  # Default to first category
            
            logger.info(f"Classified intent: {intent}")
            return intent
            
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return settings.INTENT_CATEGORIES[0]  # Default fallback
    
    async def process_data(self, intent: str, user_prompt: str, table_data: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
        """Process table data based on classified intent."""
        try:
            # TEMPORARY: Only enable transformation function for debugging
            # Force all requests to use transformation function
            logger.info(f"Processing with transformation function (intent was: {intent})")
            ai_message, processed_data = await self._transform_data(user_prompt, table_data)
            
            logger.info(f"Final Processed data before sending the response: {processed_data}")
            return ai_message, processed_data
            
            # Original code (commented out for debugging):
            # processing_functions = {
            #     "data_filtering": self._filter_data,
            #     "data_transformation": self._transform_data,
            #     "data_analysis": self._analyze_data
            # }
            # 
            # processing_func = processing_functions.get(intent, self._filter_data)
            # ai_message, processed_data = await processing_func(user_prompt, table_data)
            # 
            # return ai_message, processed_data
            
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            return f"I encountered an error while processing your request: {str(e)}", table_data
    
    async def _filter_data(self, user_prompt: str, table_data: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
        """Filter table data based on user prompt."""
        system_prompt = """
        You are a data filtering assistant. Based on the user's request, filter the provided table data.
        Return the filtered data in JSON format and provide a brief explanation of what was filtered.
        
        Format your response as:
        FILTERED_DATA: [json array of filtered items]
        EXPLANATION: [brief explanation of filtering applied]
        """
        
        data_str = str(table_data)
        full_prompt = f"User request: {user_prompt}\n\nTable data: {data_str}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=full_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return self._parse_llm_response(response.content, table_data)
    
    async def _transform_data(self, user_prompt: str, table_data: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
        """Transform table data based on user prompt."""
        system_prompt = """
        You are a data transformation assistant. Based on the user's request, modify the provided table data.
        User query will require you to create additional field(s) in order to fulfill users requests. This can be done by addition of key-value pair in each of the data object inside of the array.
        
        CRITICAL JSON FORMATTING RULES:
        1. Return ONLY valid JSON array format
        2. Do NOT add any extra text, explanations, or comments within the JSON
        3. Do NOT add content after the JSON array
        4. Ensure all JSON is properly formatted with correct commas and brackets
        5. Every transformation must include a "reasoning" field explaining the changes
        
        For example, if table_data input is:
        [
          {
            "name": "kabir"
          },
          {
            "name": "ivan"
          }
        ]
        
        And user requests "categorize each name based on likeliest nationality", return:
        [
          {
            "name": "kabir",
            "name_nationality": "Indian",
            "reasoning": "Kabir is a common name in India"
          },
          {
            "name": "ivan",
            "name_nationality": "Russian",
            "reasoning": "Ivan is a common name for Russian boys"
          }
        ]
        
        Format your response EXACTLY as:
        {
          "TRANSFORMED_DATA": [valid JSON array only]
          "EXPLANATION": [brief explanation of transformations applied]
        }
        """
        
        data_str = str(table_data)
        full_prompt = f"User request: {user_prompt}\n\nTable data: {data_str}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=full_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        logger.info(f"Response while data transformation: {response.content}")
        return self._parse_llm_response(response.content, table_data)
    
    async def _analyze_data(self, user_prompt: str, table_data: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
        """Analyze table data based on user prompt."""
        system_prompt = """
        You are a data analysis assistant. Based on the user's request, analyze the provided table data.
        Return the original data with any additional analysis columns, and provide insights.
        
        Format your response as:
        ANALYZED_DATA: [json array with original data plus analysis]
        EXPLANATION: [brief explanation of analysis performed]
        """
        
        data_str = str(table_data)
        full_prompt = f"User request: {user_prompt}\n\nTable data: {data_str}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=full_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return self._parse_llm_response(response.content, table_data)
    
    def _parse_llm_response(self, response_content: str, fallback_data: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
        import json

        try:
            # Try to parse the response as JSON directly
            jsonData = json.loads(response_content)
        except Exception:
            # If direct parsing fails, try to extract the JSON object from the string
            import re
            match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if match:
                jsonData = json.loads(match.group(0))
            else:
                # Fallback: return the fallback data and a message
                return "Could not parse LLM response as JSON.", fallback_data

        # Try to extract the correct keys, fallback to other keys if needed
        transformed_data = jsonData.get("TRANSFORMED_DATA") or jsonData.get("FILTERED_DATA") or jsonData.get("ANALYZED_DATA") or fallback_data
        explanation = jsonData.get("EXPLANATION", "")

        return explanation, transformed_data
    


    def _normalize_contact_signals(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize contact signal data types."""
        normalized = []
        for item in data:
            normalized_item = {}
            for key, value in item.items():
                # Convert known fields to proper types
                if key == 'confidence':
                    normalized_item[key] = int(value) if isinstance(value, (str, float)) else value
                elif key in ['actionTaken', 'isNew']:
                    normalized_item[key] = bool(value) if isinstance(value, (str, int)) else value
                elif key == 'timestamp' and isinstance(value, str):
                    # Ensure timestamp is a string
                    normalized_item[key] = str(value)
                else:
                    normalized_item[key] = value
            normalized.append(normalized_item)
        return normalized
