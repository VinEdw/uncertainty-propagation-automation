import math

def get_leading_place_value(value):
    """Get the leading place value of the input number."""
    # The one's place would be 0; The hundredth's place would be -2; The thousand's place would be 3
    # Ten raised to what power gives the order of magnitude of the number
    if value == 0:
        return 0 # If the number is 0, the formula breaks, so just return zero
    else:
        return math.floor(math.log(abs(value), 10))

def round_to_sig_figs(value, sig_figs):
    """
    Round the input value to the specified number of significant figures.
    Return the rounded value.
    """
    place_value = get_leading_place_value(value)
    return round(value, -(place_value - sig_figs + 1))

def get_measurement_str(value, uncertainty, separator="±"):
    """
    Return a string of the form 'value ± uncertainty'.
    The separator can be specified to some other string besides "±" if desired.
    Round the uncertainty to 1 significant figure.
    Round the value to the appropriate number of signicant figures to match the uncertainty.
    - If the uncertainty is 0, use the unrounded value
    - If the uncertainty is larger than the value, round the value to 2 significant figures
    - Otherwise, round the value to the same place value as the uncertainty
    """
    rounded_uncertainty = round_to_sig_figs(uncertainty, 1)
    if value == 0:
        rounded_value = value
    elif uncertainty > abs(value):
        rounded_value = round_to_sig_figs(value, 2)
    else:
        uncertainty_pv = get_leading_place_value(rounded_uncertainty)
        rounded_value = round(value, -uncertainty_pv)
    return f"{rounded_value} {separator} {uncertainty}"

def print_results(instructions, table_format):
    """
    Based on a processed instructions object, print out the specified tables
    Use the desired table format (markdown, latex).
    """