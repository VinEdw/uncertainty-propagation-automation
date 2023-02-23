import json
from jsonschema import validate
from sympy.parsing.sympy_parser import parse_expr

def open_json(file_name):
    """
    Open the json file at the location `file_name`.
    """
    with open(file_name, encoding="utf-8") as file:
        file_json = json.load(file)
    return file_json

def validate_json_instructions(instructions):
    """
    Check that the json instructions are valid structurally and semantically.
    Raise an error if it fails any of the checks.
    First check it against a json schema.
    Then perform the following other checks
    - All the lists of values have the same length
    - All the symbols are unique and are valid identifiers
    - All the uncertainty formulas do not reference non constant symbols besides themselves
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
                        "value": {"type": ["number", "string"]},
                        "uncertainty": {"type": "number"},
                        "units": {"type": "string"},
                    },
                    "required": ["symbol", "value", "uncertainty", "units"],
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
                    },
                    "required": ["symbol", "value", "uncertainty", "units"],
                }
            },
            "outputs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "value": {
                            "type": ["string", "array"],
                            "items": {"type": "string"}
                        },
                        "units": {"type": "string"},
                    },
                    "required": ["symbol", "value", "units"],
                }
            },
            "tables": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    }
                }
            },
        },
        "required": ["constants", "inputs", "outputs", "tables"],
    }
    validate(instructions, instruction_schema)

    # Check all the lists of values have the same length
    input_items = instructions["inputs"]
    output_items = [item for item in instructions["outputs"] if type(item["value"]) is list]
    target_length = len(input_items[0]["value"])
    for item in input_items + output_items:
        item_length = len(item["value"])
        if item_length != target_length:
            raise ValueError("The value lists used in json instructions do not all have the same length")

    # Check all the symbols are unique and are valid identifiers
    used_symbols = []
    instruction_sections = ["constants", "inputs", "outputs"]
    for section in instruction_sections:
        for item in instructions[section]:
            symbol = item["symbol"]
            if not symbol.isidentifier():
                raise ValueError(f"The symbol '{symbol}' is not a valid identifier.")
            if symbol not in used_symbols:
                used_symbols.append(symbol)
            else:
                raise ValueError(f"The symbol '{symbol}' is used for more than one item.")

    # Check all the uncertainty formulas do not reference non constant symbols besides themselves
    constant_symbol_list = [item["symbol"] for item in instructions["constants"]]
    for item in instructions["inputs"]:
        symbol = item["symbol"]
        uncertainty_formula = parse_expr(item["uncertainty"])
        for var in uncertainty_formula.free_symbols:
            if str(var) not in (constant_symbol_list + [symbol]):
                raise ValueError(f"The uncertainty formula for '{symbol}' references a non constant symbol besides itself.")

def load_instructions(file_name):
    """
    Load the json instructions for what to calculate.
    This includes the symbols, values, uncertainty, and units for the constants ("constants") and raw data ("inputs").
    It also includes the symbols, formulas, and units for the calculated quantities ("outputs"),
    Lastly, it optionally includes information on what tables to print out ("tables").
    
    Validate that the json file is structurally and semantically sound.
    
    Return the json instructions object.
    """
    instructions = open_json(file_name)
    validate_json_instructions(instructions)
    return instructions
