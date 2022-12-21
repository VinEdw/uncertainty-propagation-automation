import json
from jsonschema import validate

def open_json_instructions(file_name):
    """
    Open the file at the location `file_name`.
    This should be a .json file with the instructions for what to calculate.
    This includes the symbols, values, uncertainty, and units for the constants ("constants") and raw data ("inputs").
    It also includes the symbols, formulas, and units for the calculated quantities ("outputs"),
    """
    with open(file_name) as file:
        file_json = json.load(file)
    return file_json

def validate_json_instructions(insturctions):
    """
    Check that the json instructions are valid structurally and semantically.
    Raise an error if it fails any of the checks.
    First check it against a json schema.
    Then perform the following other checks
    - 
    """
    instruction_schema = {
        "type": "object",
        "properties": {
            "constants": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "value": {"type": "number"},
                        "uncertainty": {"type": "number"},
                        "units": {"type": "string"},
                    }
                }
            },
            "inputs": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "value": {"type": "array", "items": {"type": "number"}},
                        "uncertainty": {"type": "string"},
                        "units": {"type": "string"},
                    }
                }
            },
            "outputs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "value": {"type": "string"},
                        "units": {"type": "string"},
                    }
                }
            },
            "tables": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        }
                    }
                }
            },
        }
    }
    validate(insturctions, instruction_schema)

