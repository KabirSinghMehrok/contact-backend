#!/usr/bin/env python3
"""Test script for the new LLM response parsing function."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.llm_service import LLMService
import logging

# Set up logging to see the debug output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_parsing():
    """Test the parsing function with the provided example."""
    
    # Example response content from the user
    response_content = """TRANSFORMED_DATA: [
  {
    "id": "f2d9969a-b1cb-4dd2-bb5d-099d217aa2c3",
    "prospectName": "Herbert Runolfsdottir",
    "company": "Wilderman - Medhurst",
    "title": "Direct Quality Analyst",
    "signalType": "tech_adoption",
    "urgency": "medium",
    "industry": "Automotive",
    "companySize": "1-50",
    "description": "Migrated to Cloud Infrastructure platform",
    "timestamp": "2025-08-20T15:51:33.591Z",
    "confidence": 80,
    "actionTaken": false,
    "nationality": "Icelandic",
    "reasoning": "Runolfsdottir is an Icelandic surname"
  },
  {
    "id": "a66d3de7-9487-4140-bb5f-5b4075ac26bd",
    "prospectName": "Dr. Jermaine Bins PhD",
    "company": "Hickle Group",
    "title": "Senior Solutions Executive",
    "signalType": "hiring",
    "urgency": "medium",
    "industry": "Hospitality",
    "companySize": "1-50",
    "description": "Recruiting 6 Product Manager professionals for North Thurmanburgh office",
    "timestamp": "2025-08-20T02:24:40.239Z",
    "confidence": 83,
    "actionTaken": false,
    "nationality": "American",
    "reasoning": "Name sounds American"
  },
  {
    "id": "b96702f1-aa93-4738-9c3c-fd817bed510d",
    "prospectName": "Francis Ratke",
    "company": "Kessler - Borer",
    "title": "Dynamic Functionality Architect",
    "signalType": "intent",
    "urgency": "high",
    "industry": "Media & Entertainment",
    "companySize": "1-50",
    "description": "Evaluating CRM tools and platforms",
    "timestamp": "2025-08-15T14:39:09.463Z",
    "confidence": 86,
    "actionTaken": false,
    "nationality": "German",
    "reasoning": "Ratke is a German surname"
  }
]
EXPLANATION: Added a new field called "nationality" to each object in the array. The reasoning for each nationality assignment is also provided. Note that these nationalities are based on common name associations and may not be entirely accurate."""

    # Create a mock LLMService instance (we only need the parsing method)
    class MockLLMService:
        def _parse_llm_response(self, response_content: str, fallback_data):
            # Copy the parsing logic from the actual service
            import json
            import re
            import logging
            
            logger = logging.getLogger(__name__)
            
            logger.info("Starting LLM response parsing")
            logger.info(f"Response content length: {len(response_content)} characters")
            logger.debug(f"Full response content: {response_content}")
            
            try:
                # Initialize defaults
                explanation = "Data processed successfully."
                data = fallback_data
                
                # Extract explanation using regex
                explanation_match = re.search(r'EXPLANATION:\s*(.+?)(?=\n\n|\Z)', response_content, re.DOTALL)
                if explanation_match:
                    explanation = explanation_match.group(1).strip()
                    logger.info(f"Found explanation: {explanation}")
                else:
                    logger.warning("No explanation found in response")
                
                # Extract data using regex - look for TRANSFORMED_DATA: followed by JSON array
                data_patterns = [
                    r'TRANSFORMED_DATA:\s*(\[.*?\])',
                    r'FILTERED_DATA:\s*(\[.*?\])', 
                    r'ANALYZED_DATA:\s*(\[.*?\])'
                ]
                
                for pattern in data_patterns:
                    data_match = re.search(pattern, response_content, re.DOTALL)
                    if data_match:
                        json_str = data_match.group(1).strip()
                        logger.info(f"Found JSON data with pattern: {pattern}")
                        logger.debug(f"JSON string to parse: {json_str[:200]}...")
                        
                        try:
                            parsed_data = json.loads(json_str)
                            logger.info(f"Successfully parsed JSON with {len(parsed_data)} items")
                            data = parsed_data
                            break  # Stop after first successful match
                        except json.JSONDecodeError as e:
                            logger.warning(f"JSON parsing failed: {e}")
                            logger.warning(f"Problematic JSON: {json_str[:300]}...")
                            
                            # Try to clean up the JSON string
                            cleaned_json = self._clean_json_string(json_str)
                            if cleaned_json:
                                try:
                                    parsed_data = json.loads(cleaned_json)
                                    logger.info(f"Successfully parsed cleaned JSON with {len(parsed_data)} items")
                                    data = parsed_data
                                    break
                                except json.JSONDecodeError as e2:
                                    logger.error(f"Even cleaned JSON parsing failed: {e2}")
                else:
                    logger.warning("No valid data pattern found in response")
                
                logger.info(f"Parsing complete - explanation: '{explanation}', data items: {len(data)}")
                return explanation, data
                
            except Exception as e:
                logger.error(f"Unexpected error in LLM response parsing: {e}")
                logger.error(f"Response content that caused error: {response_content}")
                return "Data processed with some issues.", fallback_data
        
        def _clean_json_string(self, json_str: str) -> str:
            """Clean common JSON formatting issues."""
            import re
            import logging
            
            logger = logging.getLogger(__name__)
            logger.info("Attempting to clean JSON string")
            
            # Remove any trailing text after the closing bracket
            cleaned = re.sub(r'\][\s\S]*$', ']', json_str)
            
            # Remove any leading text before the opening bracket
            cleaned = re.sub(r'^[\s\S]*?\[', '[', cleaned)
            
            # Fix trailing commas before } or ]
            cleaned = re.sub(r',\s*}', '}', cleaned)
            cleaned = re.sub(r',\s*]', ']', cleaned)
            
            # Fix missing commas between objects
            cleaned = re.sub(r'}\s*{', '},{', cleaned)
            
            # Remove any extra whitespace/newlines that might cause issues
            cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
            
            logger.info(f"JSON cleaning complete. Original length: {len(json_str)}, Cleaned length: {len(cleaned)}")
            return cleaned
    
    # Test the parsing
    mock_service = MockLLMService()
    fallback_data = []
    
    print("Testing LLM response parsing...")
    print("=" * 50)
    
    explanation, data = mock_service._parse_llm_response(response_content, fallback_data)
    
    print(f"\nExplanation: {explanation}")
    print(f"Number of data items: {len(data)}")
    
    if data:
        print("\nFirst data item:")
        import json
        print(json.dumps(data[0], indent=2))
        
        print(f"\nAll items have 'nationality' field: {all('nationality' in item for item in data)}")
        print(f"All items have 'reasoning' field: {all('reasoning' in item for item in data)}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_parsing()
