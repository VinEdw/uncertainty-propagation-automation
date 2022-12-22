import math
from instruction_processor import get_item

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

def item_to_column(item, header_format="{symbol} ({units})", separator="±", bar_after_header=True):
    """
    Convert the information for the given item into a list of strings representing the data it contains.
    These strings will all be left justified to the same length.
    Each value-uncertainty pair will be turned into a string using get_measurement_str() ('separator' can be specified).
    The header will be formated with the specified format string ('symbol' and 'units' will be used as replacements).
    Optionally, a bar of hyphens like "----" can be placed after the header.
    """
    column = []
    symbol = item["symbol"]
    units = item["units"]
    header = header_format.format(symbol=symbol, units=units)
    column.append(header)
    for value, uncertainty in zip(item["value"], item["uncertainty"]):
        measurement_str = get_measurement_str(value, uncertainty, separator)
        column.append(measurement_str)
    max_length = max(len(cell) for cell in column)
    column = [cell.ljust(max_length) for cell in column]
    if bar_after_header:
        bar = "-" * max_length
        column.insert(1, bar)
    return column
        

def print_results(instructions, table_format):
    """
    Based on a processed instructions object, print out the specified tables
    Use the desired table format (markdown, latex).
    """