import json

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
