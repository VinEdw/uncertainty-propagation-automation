import json
from jsonschema import validate
from sympy.parsing.sympy_parser import parse_expr

def open_json_instructions(file_name):
    """
    Open the file at the location `file_name`.
    This should be a .json file with the instructions for what to calculate.
    This includes the symbols, values, uncertainty, and units for the constants ("constants") and raw data ("inputs").
    It also includes the symbols, formulas, and units for the calculated quantities ("outputs"),
    Lastly, it optionally includes information on what tables to print out ("tables").
    """
    with open(file_name) as file:
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
    - All the uncertainty formulas do not reference symbols besides themselves
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
                        "type": "string",
                    }
                }
            },
        }
    }
    validate(instructions, instruction_schema)

    # Check all the lists of values have the same length
    input_items = instructions["inputs"]
    target_length = len(input_items[0]["value"])
    for item in input_items:
        item_length = len(item["value"])
        if item_length != target_length:
            raise ValueError("The value lists for the items in the 'inputs' section of the json instructions do not all have the same length")

    # Check all the symbols are unique and are valid identifiers
    used_symbols = []
    instruction_sections = ["constants","inputs", "outputs"]
    for section in instruction_sections:
        for item in instructions[section]:
            symbol = item["symbol"]
            if not symbol.isidentifier():
                raise ValueError(f"The symbol '{symbol}' is not a valid identifier.")
            if symbol not in used_symbols:
                used_symbols.append(symbol)
            else:
                raise ValueError(f"The symbol '{symbol}' is used for more than one item.")

    # Check all the uncertainty formulas do not reference symbols besides themselves
    for item in instructions["inputs"]:
        symbol = item["symbol"]
        uncertainty_formula = parse_expr(item["uncertainty"])
        var_str_list = [str(var) for var in uncertainty_formula.free_symbols]
        if len(var_str_list) == 1:
            if symbol not in var_str_list:
                raise ValueError(f"The uncertainty formula for '{symbol}' references a symbol besides itself.")
        if len(var_str_list) > 1:
            raise ValueError(f"The uncertainy formula for '{symbol}' references multiple symbols.")

def load_instructions(file_name):
    """
    Load the json instructions for what to calculate.
    This includes the symbols, values, uncertainty, and units for the constants ("constants") and raw data ("inputs").
    It also includes the symbols, formulas, and units for the calculated quantities ("outputs"),
    Lastly, it optionally includes information on what tables to print out ("tables").
    
    Validate that the json file is structurally and semantically sound.
    
    Return the json instructions object.
    """
    instructions = open_json_instructions(file_name)
    validate_json_instructions(instructions)
    return instructions
