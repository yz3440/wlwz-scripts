import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
context_prompt = """
Parse this single scene from 武林外传 into a JSON object following these specifications:

Scene Object Types:
1. Normal Scene:
{
  "type": "normal",
  "rawDescription": "Original scene description", 
  "location": "Physical setting", 
  "timeOfDay": "Time indicator",
  "context": "Additional context (if present)", 
  "performances": [...]
}

2. Cutscene:
{
  "type": "cutscene",
  "rawDescription": "Original scene description", // eg. 【过场，点穴记】
  "cutSceneName": "Name of the cutscene" // eg. 点穴记
  "plot": "Optional plot of the cutscene" // eg. 治腿记
}

Scene Description Parsing:
- Normal scene format: 【location，timeOfDay】 or 【context，location，timeOfDay】
  Examples:
  - "【现代，平谷飞龙影视基地，昼】" → context: "现代", location: "平谷飞龙影视基地"
  - "【广告，大堂，昼】" → context: "广告", location: "大堂"
- Cutscene format: 【过场，cutSceneName】

Performances Array (for normal scenes):
1. Dialog Object:
   {
     "type": "dialog",
     "speaker": "Character name",
     "performances": [
       {
         "type": "line",
         "line": "Actual dialogue"
       },
       {
         "type": "speaker-action",
         "description": "Action text"
       }
     ]
   }

2. Action Object:
   {
     "type": "action",
     "description": "Action description"
   }

Formatting Rules:
1. Preserve original Chinese punctuation
2. Add missing sentence-ending punctuation where needed
3. Remove parentheses from action descriptions
4. Remember to escape every quotation marks in the dialog or action. (IMPORTANT!!)
5. Keep action text verbatim, no missing texts, no paraphrasing (IMPORTANT!!)
6. Multiple speakers for one line should be combined into a single string
7. Ignore the "本回完" text in the last line of the last scene. Ignore page numbers (a number as it's own line)
8. In these episode, “展堂” and "白展堂" are the different characters. “展堂” is noted in the dialog often as "展 堂“. Please keep the difference.

Action vs Speaker-Action:
- If an action is clearly performed by the speaking character → "speaker-action" (speaker-action lives under "performances" -> "dialog" -> "performances")
- If the action is general or performed by others → "action" (action lives under "performances")
- Use context to determine classification
"""


def build_prompt(scene_text: str) -> str:
    return (
        context_prompt
        + "\n\nHere's the script:\n\n"
        + scene_text
        + "\n\n"
        + "Please parse the script into a sensible json format with NO INDENTS. "
        + "Please just return the full json, no other text."
    )


def extract_json(response):
    import json

    json_start = response.index("{")
    json_end = response.rfind("}")

    res = json.loads(response[json_start : json_end + 1])
    return res


# Load environment variables from .env file
load_dotenv()


def llm_parse_scene(scene_text: str, anthropic_api_key: str) -> str:
    if not anthropic_api_key:
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        raise ValueError("Anthropic API key is not set")

    client = Anthropic(api_key=anthropic_api_key)
    response = client.messages.create(
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": build_prompt(scene_text),
            }
        ],
        model="claude-3-5-sonnet-latest",
    )

    single_message = response.content[0].text
    return single_message


def find_missing_parts(parsed_text: str, original_text: str):
    """
    Tests if all parts of the original scene text are present in the parsed JSON output.
    """
    original_text_lines = original_text.split("\n")
    parsed_text_lines = parsed_text.split("\n")

    original_parts = []
    for line in original_text_lines:
        import re

        parts = re.split(r"[（）—().,!?;:，。！？；：、„~【】…]", line)
        for part in parts:
            part = part.strip()
            if part != "" and part != None:
                original_parts.append(part)

    # check if every part is in the parsed scene
    missing_parts = []
    for part in original_parts:
        if part not in parsed_text:
            missing_parts.append(part)

    return missing_parts


import json
import jsonschema
from jsonschema import validate, ValidationError
from typing import Union

# Define the schema for the "normal" scene type
normal_scene_schema = {
    "type": "object",
    "required": ["type", "rawDescription", "location", "timeOfDay", "performances"],
    "properties": {
        "type": {"type": "string", "enum": ["normal"]},
        "rawDescription": {"type": "string"},
        "location": {"type": "string"},
        "timeOfDay": {"type": ["string", "null"]},
        "context": {"type": ["string", "null"]},
        "performances": {
            "type": "array",
            "items": {
                "type": "object",
                "oneOf": [
                    {
                        "type": "object",
                        "required": ["type", "description"],
                        "properties": {
                            "type": {"type": "string", "enum": ["action"]},
                            "description": {"type": "string"},
                        },
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "required": ["type", "speaker", "performances"],
                        "properties": {
                            "type": {"type": "string", "enum": ["dialog"]},
                            "speaker": {"type": "string"},
                            "performances": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "oneOf": [
                                        {
                                            "type": "object",
                                            "required": ["type", "line"],
                                            "properties": {
                                                "type": {
                                                    "type": "string",
                                                    "enum": ["line"],
                                                },
                                                "line": {"type": "string"},
                                            },
                                            "additionalProperties": False,
                                        },
                                        {
                                            "type": "object",
                                            "required": ["type", "description"],
                                            "properties": {
                                                "type": {
                                                    "type": "string",
                                                    "enum": ["speaker-action"],
                                                },
                                                "description": {"type": "string"},
                                            },
                                            "additionalProperties": False,
                                        },
                                    ],
                                },
                                "minItems": 1,
                            },
                        },
                        "additionalProperties": False,
                    },
                ],
            },
            "minItems": 1,
        },
    },
    "additionalProperties": False,
}

# Define the schema for the "cutscene" type
cutscene_schema = {
    "type": "object",
    "required": ["type", "rawDescription", "cutSceneName"],
    "properties": {
        "type": {"type": "string", "enum": ["cutscene"]},
        "rawDescription": {"type": "string"},
        "cutSceneName": {"type": "string"},
        "plot": {"type": "string"},  # Optional field
    },
    "additionalProperties": False,
}


def validate_scene_script_json(json_data: Union[dict, str]) -> bool:
    """
    Validate the provided JSON data against both screenplay schemas.
    The JSON is considered valid if it passes either schema.

    Args:
        json_data (Union[dict, str]): JSON data to validate, either as a Python dict or JSON string

    Returns:
        bool: True if validation succeeds against either schema

    Raises:
        jsonschema.exceptions.ValidationError: If validation fails against both schemas
        json.JSONDecodeError: If json_data is a string and not valid JSON
    """
    # If input is a string, parse it as JSON
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    # Try to validate against the normal scene schema
    try:
        validate(instance=json_data, schema=normal_scene_schema)
        return True
    except ValidationError as e:
        normal_error = e

    # If that fails, try to validate against the cutscene schema
    try:
        validate(instance=json_data, schema=cutscene_schema)
        return True
    except ValidationError as e:
        cutscene_error = e

    # If we get here, the JSON failed both validations
    raise ValidationError(
        f"JSON failed validation against both schemas.\n"
        f"Normal scene error: {normal_error.message}\n"
        f"Cutscene error: {cutscene_error.message}"
    )
