#!/usr/bin/env python3
"""Simple test script for the new LLM response parsing function."""

import json
import re
import logging

# Set up logging to see the debug output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_json_string(json_str: str) -> str:
    """Clean common JSON formatting issues."""
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

def parse_llm_response(response_content: str, fallback_data):
    """Parse LLM response and extract data and explanation."""
    import json
    
    # Extract explanation
    explanation = "Data processed successfully."
    data = fallback_data
    
    if "EXPLANATION:" in response_content:
        explanation = response_content.split("EXPLANATION:")[-1].strip()
    
    # Find JSON array after TRANSFORMED_DATA: - much simpler approach
    if "TRANSFORMED_DATA:" in response_content:
        # Split on TRANSFORMED_DATA: and take everything after it
        after_transformed = response_content.split("TRANSFORMED_DATA:")[1]
        
        # Find the opening bracket
        bracket_start = after_transformed.find("[")
        if bracket_start != -1:
            # Find the matching closing bracket by counting
            bracket_count = 0
            for i, char in enumerate(after_transformed[bracket_start:]):
                if char == "[": 
                    bracket_count += 1
                elif char == "]": 
                    bracket_count -= 1
                    if bracket_count == 0:
                        # Found the end of the JSON array
                        json_str = after_transformed[bracket_start:bracket_start+i+1]
                        try:
                            data = json.loads(json_str)
                            logger.info(f'Successfully parsed JSON with {len(data)} items')
                            return explanation, data
                        except json.JSONDecodeError as e:
                            logger.error(f'JSON parsing failed: {e}')
                            logger.error(f'JSON string: {json_str[:200]}...')
    
    return explanation, data

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

    fallback_data = []
    
    print("Testing LLM response parsing...")
    print("=" * 50)
    
    explanation, data = parse_llm_response(response_content, fallback_data)
    
    print(f"\nExplanation: {explanation}")
    print(f"Number of data items: {len(data)}")
    
    if data:
        print("\nFirst data item:")
        print(json.dumps(data[0], indent=2))
        
        print(f"\nAll items have 'nationality' field: {all('nationality' in item for item in data)}")
        print(f"All items have 'reasoning' field: {all('reasoning' in item for item in data)}")
        
        print(f"\nNationalities found: {[item.get('nationality') for item in data]}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_parsing()
