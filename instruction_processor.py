from sympy.parsing.sympy_parser import parse_expr

def get_item(instructions, symbol):
    """
    Return the item with the given symbol from the instructions object.
    """
    instruction_sections = ["constants", "inputs", "outputs"]
    for section in instruction_sections:
        for item in instructions[section]:
            if symbol == item["symbol"]:
                return item
    raise KeyError(f"Symbol '{symbol}' not in instructions object.")

def get_constant_substitutions(instructions):
    """
    Return a substitutions dictionary for all the constants.
    """
    substitutions = {}
    for item in instructions["constants"]:
        symbol = item["symbol"]
        value = item["value"]
        substitutions[symbol] = value
    return substitutions

def get_substitutions(instructions, formula, row):
    """
    Return a substitutions dictionary for the given formula at the given row.
    """
    substitutions = get_constant_substitutions(instructions)
    for var in formula.free_symbols:
        symbol = str(var)
        if symbol in substitutions:
            continue
        item = get_item(instructions, symbol)
        value = item["value"][row]
        substitutions[symbol] = value
    return substitutions

def process_instructions(instructions):
    """
    Process the calculation instructions.
    "instructions" is the processed json input file.
    Note that the instructions object will be mutated in the process.
    
    Tasks include calculating the uncertainty for each input item, and calculating the values & uncertainty for each output item.
    """