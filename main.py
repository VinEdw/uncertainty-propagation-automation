import sys
import math
from instruction_loader import open_json_instructions
from sympy.parsing.sympy_parser import parse_expr

def validate_data(data):
    """Check that the structure of the json data is correct."""
    # Check that all the manually entered lists of values have the same lengths
    # It is assumed that there is at least one input symbol
    inputs = data["inputs"]
    target_length = len(inputs[0]["value"])
    for item in inputs:
        current_length = len(item["value"])
        if current_length != target_length:
            return False
    # Check that all the symbols are unique
    symbol_set = set()
    symbol_count = 0
    for item in data["constants"] + data["inputs"] + data["outputs"]:
        symbol_count += 1
        symbol_set.add(item["symbol"])
    if symbol_count != len(symbol_set):
        return False
    # If all checks pass, return True
    # Note: More checks can be added in the future if desired
    return True

def calculate_input_uncertainty(data):
    """Calculate the uncertainty for each value in the input section of the json data."""
    # The uncertainty for each item/quantity in the input section of the json data is given as a formula
    # This formula gets turned into list of specific uncertainty values, one for each measured value
    for item in data["inputs"]:
        # Grab the needed info from the json data on the current quantity
        symbol = item["symbol"]
        value_list = item["value"]
        uncertainty_formula = parse_expr(item["uncertainty"]) # Parse the formula
        uncertainty_list = []
        for value in value_list:
            # Use the constants and the current measured value as substitutions when evaluating the uncertainty
            substitutions = {item["symbol"]:item["value"] for item in data["constants"]}
            substitutions[symbol] = value
            uncertainty = uncertainty_formula.evalf(subs=substitutions)
            uncertainty_list.append(uncertainty)
        item["uncertainty"] = uncertainty_list

def get_row_data(data, row):
    """Get the values and uncertainties for a single row of data."""
    row_data = {}
    # Grab the stuff in the constants section
    for item in data["constants"]:
        symbol = item["symbol"]
        row_data[symbol] = {
            "value": item["value"],
            "uncertainty": item["uncertainty"],
            # "units": item["units"]
        }
    # Grab the stuff in the inputs section at the given row
    for item in data["inputs"]:
        symbol = item["symbol"]
        row_data[symbol] = {
            "value": item["value"][row],
            "uncertainty": item["uncertainty"][row],
            # "units": item["units"]
        }
    # Grab the data in the outputs section at the given row (but only if it has been evaluated already)
    for item in data["outputs"]:
        symbol = item["symbol"]
        # Skip this quantity if its value is still a formula string
        if type(item["value"]) == str:
           continue 
        row_data[symbol] = {
            "value": item["value"][row],
            "uncertainty": item["uncertainty"][row],
            # "units": item["units"]
        }
    return row_data

def get_row_substitutions(row_data):
    """Create a substitution dictionary based on the row data."""
    return {key:data["value"] for key, data in row_data.items()}

def calculate_output(data):
    """Calculate the value and uncertainty for each of the quantities in the output section of the json data."""
    row_count = len(data["inputs"][0]["value"])
    # Iterate through each of the output quantities
    for item in data["outputs"]:
        formula = parse_expr(item["value"])
        var_set = formula.free_symbols
        value_list = []
        uncertainty_list = []
        # Iterate through each row
        for i in range(row_count):
            row_data = get_row_data(data, i)
            row_substitutions = get_row_substitutions(row_data)
            error_contributions = []
            # Iterate through each variable in the formula used to calculate the quantities value
            for x in var_set:
                partial_x = formula.diff(x).evalf(subs=row_substitutions) # Take the partial derivative of the formula with respect to the variable; evaluate it
                delta_x = row_data[str(x)]["uncertainty"] # Fetch the variable's uncertainty
                error_x = partial_x * delta_x # Multiply the partial derivative and the variable's uncertainty
                error_x_squared = error_x **2 # Square it
                error_contributions.append(error_x_squared) # Put the squared error in the list
            value = formula.evalf(subs=row_substitutions)
            uncertainty = sum(error_contributions)**0.5 # The uncertainty is each of the uncertainty contributions added in quadrature
            value_list.append(value)
            uncertainty_list.append(uncertainty)
        item["value"] = value_list
        item["uncertainty"] = uncertainty_list

def get_leading_place_value(value):
    """Get the leading place value of the input number."""
    # The one's place would be 0; The hundredth's place would be -2; The thousand's place would be 3
    # Ten raised to what power gives the order of magnitude of the number
    if value == 0:
        return 0 # If the number is 0, the formula breaks, so just return zero
    else:
        return math.floor(math.log(abs(value), 10))

def round_uncertainty(uncertainty):
    """Round the uncertainty to one significant figure."""
    place_value = get_leading_place_value(uncertainty)
    return round(uncertainty, -place_value)

def round_value_to_uncertainty(value, uncertainty):
    """Round a value to match the given uncertainty."""
    # If the uncertainty is 0, return the unrounded value
    if uncertainty == 0:
        return value
    # If the uncertainty is larger than the value, return the value to 2 significant figures
    if uncertainty > abs(value):
        value_pv = get_leading_place_value(value)
        return round(value, -(value_pv-1))
    # Otherwise, round the value to the same place value as the uncertainty
    rounded_uncertainty = round_uncertainty(uncertainty)
    uncertainty_pv = get_leading_place_value(rounded_uncertainty)
    return round(value, -uncertainty_pv)

def get_symbol_from_data(data, symbol):
    """Grab the dictionary for the given symbol string from the json data."""
    for item in data["inputs"] + data["outputs"]:
        if symbol == item["symbol"]:
            return item
    return None

def pretty_print_data(data, columns=None):
    """Make a string form of the processed data in a nice table."""
    table = []
    pm = "±"
    if columns == None:
        item_list = data["inputs"] + data["outputs"]
    else:
        item_list = [get_symbol_from_data(data, symbol) for symbol in columns]

    for item in item_list:
        symbol = item["symbol"]
        units = item["units"]
        header = f"{symbol} ({units})"
        column_strs = [header]
        # Round each value/uncertainty pair and put them in a string together
        # Collect these strings in a list
        for value, uncertainty in zip(item["value"], item["uncertainty"]):
            rounded_value = round_value_to_uncertainty(float(value), float(uncertainty))
            rounded_uncertainty = round_uncertainty(float(uncertainty))
            column_strs.append(f"{rounded_value} {pm} {rounded_uncertainty}")
        # Justify each of these strings to have the same length
        max_length = max(len(string) for string in column_strs)
        column_strs = [string.ljust(max_length) for string in column_strs]
        # Add a horizontal bar after the header
        column_strs.insert(1, "-" * max_length)
        # Add the column string list to the table list
        table.append(column_strs)
    # Insert a trial number column at the start
    row_count = len(table[0])
    max_length = max(5, len(str(row_count)))
    trial_column = ["Trial", "-" * max_length] + [str(i) for i in range(1, row_count + 1)]
    trial_column = [string.ljust(max_length) for string in trial_column]
    table.insert(0, trial_column)
    # Construct the final string
    final_str = ""
    column_count = len(table)
    for i in range(row_count):
        row_data = []
        for j in range(column_count):
            cell = table[j][i]
            row_data.append(cell)
        row_str = " | ".join(row_data)
        final_str += row_str + "\n"
    return final_str[:-1]

def print_latex_table(data, columns):
    """Make a Latex version of the table string."""
    # Assume these macros exist, among the other ones provided by the iopart class
    # \\def\\mcm{r@{.}l@{ ± }r@{.}l}
    # \\def\\mch#1{\multicolumn{4}{l}{#1}} 
    starting_str = pretty_print_data(data, columns)
    starting_str = starting_str.replace("|", "&") # Replace vertical bars with ampersands
    starting_str = starting_str.replace(".", "&") # Replace decimal points with ampersands
    starting_str = starting_str.replace("±", "&") # Replace plus or minus with ampersands
    split_str = starting_str.split("\n")
    split_str[1] = "\mr" # Replace the horizontal bar with "\mr"
    # Add \\ to the end of each data row
    for i in range(2, len(split_str)):
        split_str[i] += "\\\\"
    # Make the headers multicolumn
    split_header = split_str[0].split(" & ")
    column_count = len(split_header)
    new_split_header = []
    for header in split_header:
        # Skip the trial header
        if header.strip() == "Trial":
            new_split_header.append("Trial ")
            continue
        header = header.strip()
        middle_space_index = header.find(" ")
        symbol = header[:middle_space_index]
        units = header[middle_space_index:]
        new_header = "\\mch{$" + symbol + "$" + units + "}"
        new_split_header.append(new_header)
    split_str[0] = "&".join(new_split_header) + "\\\\"
    # Make the opening and closing tabular syntax
    opening = "\\begin{table}[htbp]\n\caption{\label{}\n}\n"
    opening += "\\begin{indented}\\lineup\\item[]\\begin{tabular}{@{}l" + "\\mcm" * (column_count - 1) + "}\n\\br\n"
    closing = "\n\\br\n\\end{tabular}\\end{indented}\\end{table}"

    final_str = opening + "\n".join(split_str) + closing
    final_str = final_str.replace(" -", "\\-") # Fix minus signs without breaking column alignment
    return final_str


if __name__ == "__main__":
    # Open the input file name and load the data
    file_name = sys.argv[1]
    if len(sys.argv) == 3:
        table_format = sys.argv[2]
    else:
        table_format = "markdown"
    data = open_json_instructions(file_name)
    
    # Validate the data structure; Stop if it is bad
    if not validate_data(data):
        print("Invalid input")
        quit()
    
    calculate_input_uncertainty(data)
    calculate_output(data)
    
    desired_tables = data.get("tables", None)
    if desired_tables == None or len(desired_tables) == 0:
        desired_tables = [None]
    for column_list in desired_tables:
        if table_format == "markdown":
            pretty_str = pretty_print_data(data, column_list)
            print(pretty_str)
        elif table_format == "latex":
            latex_str = print_latex_table(data, column_list)
            print(latex_str)
        print()
