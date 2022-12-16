import math
from sympy.parsing.sympy_parser import parse_expr # import the formula parser from Sympy 

# A loose idea of what the JSON input might look like for the input values
# Note: Units are not used for anything yet
measurements = {
    "h": {
        "value": 94.0,
        "uncertainty": 0.2,
        "units": "cm"
    },
    "R": {
        "value": 142.0,
        "uncertainty": 0.3,
        "units": "cm"
    },
    "g": {
        "value": 981,
        "uncertainty": 0,
        "units": "cm/s^2"
    }
}

# Simplify the measurements dictionary by having the symbol point to just the value
# This will be used when substituting the values into the expression for evaluation with .evalf()
measurement_values = {}
for key, data in measurements.items():
    measurement_values[key] = data["value"]

# This is the formula that will be used
# It's for the value that we want to calculate and propagate the uncertainty of
formula_str = "sqrt(g * R**2 / (2 * h))"
formula = parse_expr(formula_str)
# This is a set containing all the variables in the formula
var_set = formula.free_symbols

# Calculate the uncertainty contributions from each of the variables in the formula
uncertainty_contributions = []
for x in var_set:
    # Take the partial derivative of the formula with respect to the variable; evaluate it
    partial_x = formula.diff(x).evalf(subs=measurement_values)
    # Fetch the variable's uncertainty
    delta_x = measurements[str(x)]["uncertainty"]
    # Multiply the partial derivative and the variable's uncertainty
    error_x = partial_x * delta_x
    # Square it
    error_x_squared = error_x **2
    # Put the squared error in the list
    uncertainty_contributions.append(error_x_squared)

# Evalute to get the result
result = formula.evalf(subs=measurement_values)
# Add all the uncertainty contributions in quadrature
uncertainty = sum(uncertainty_contributions)**0.5

def get_leading_place_value(value):
    """Get the leading place value of the leading digit of the input number."""
    return math.floor(math.log(abs(value), 10))
    
def string_to_sig_figs(value, sig_figs):
    """Retrun the string representation of the input number rounded to the desired number of significant figures."""
    return f"{value:.{sig_figs}}"

def round_to_sig_figs(value, sig_figs):
    """Round the input number to the desired number of significant figures."""
    return float(string_to_sig_figs(value, sig_figs))

# Round the uncertainty to one sig fig
uncertainty = round_to_sig_figs(uncertainty, 1)
# Round the result to match its uncertainty
uncertainty_place_value = get_leading_place_value(uncertainty)
result = round(result, -uncertainty_place_value)

# Print the answer
print(f"{result} ± {uncertainty}")