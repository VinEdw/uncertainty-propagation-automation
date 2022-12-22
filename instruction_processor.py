from sympy.parsing.sympy_parser import parse_expr

def get_row_count(instructions):
    """
    Looking at the instructions object, get the number of rows for each input and output.
    """
    return len(instructions["inputs"][0]["value"])

def get_item(instructions, symbol):
    """
    Return the item with the given symbol from the instructions object.
    """
    instruction_sections = ["inputs", "outputs", "constants"]
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

def calculate_input_uncertainty(instructions, item):
    """
    Calculate the uncertainty for each of the given input item's values.
    Note that the item object will be mutated in the process.
    """
    symbol = item["symbol"]
    uncertainty_formula = parse_expr(item["uncertainty"])
    uncertainty_list = []
    substitutions = get_constant_substitutions(instructions)
    for value in item["value"]:
        substitutions[symbol] = value
        uncertainty = uncertainty_formula.evalf(subs=substitutions)
        uncertainty_list.append(uncertainty)
    item["uncertainty"] = uncertainty_list

def calculate_output_values_and_uncertainty(instructions, item):
    """
    Calculate the values and uncertainty for the output item.
    Note that the item object will be mutated in the process.
    """
    formula = item["value"]
    value_list = []
    uncertainty_list = []
    for i in range(get_row_count(instructions)):
        substitutions = get_substitutions(instructions, formula, i)
        error_contributions = []
        # Iterate through each variable in the formula used to calculate the quantities value
        for x in formula.free_symbols:
            partial_x = formula.diff(x).evalf(subs=substitutions) # Take the partial derivative of the formula with respect to the variable; evaluate it
            delta_x = get_item(str(x))["uncertainty"] # Fetch the variable's uncertainty
            error_x = partial_x * delta_x # Multiply the partial derivative and the variable's uncertainty
            error_x_squared = error_x **2 # Square it
            error_contributions.append(error_x_squared) # Put the squared error in the list
        value = formula.evalf(subs=substitutions)
        uncertainty = sum(error_contributions)**0.5 # The full uncertainty is each of the uncertainty contributions added in quadrature
        value_list.append(value)
        uncertainty_list.append(uncertainty)
    item["value"] = value_list
    item["uncertainty"] = uncertainty_list

def process_instructions(instructions):
    """
    Process the calculation instructions.
    "instructions" is the processed json input file.
    Note that the instructions object will be mutated in the process.
    
    Tasks include calculating the uncertainty for each input item, and calculating the values & uncertainty for each output item.
    """