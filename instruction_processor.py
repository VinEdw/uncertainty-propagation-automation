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

def get_substitutions(instructions, formula, row):
    """
    Return a substitutions dictionary for the given formula at the given row.
    """
    substitutions = {}
    for var in formula.free_symbols:
        symbol = str(var)
        item = get_item(instructions, symbol)
        value_attr = item["value"]
        if type(value_attr) == list:
            value = value_attr[row]
        else:
            value = value_attr
        substitutions[symbol] = value
    return substitutions

def process_instructions(instructions):
    """
    Process the calculation instructions.
    "instructions" is the processed json input file.
    Note that the instructions object will be mutated in the process.
    
    Tasks include calculating the uncertainty for each input item, and calculating the values & uncertainty for each output item.
    """