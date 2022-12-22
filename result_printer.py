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
    return f"{rounded_value} {separator} {rounded_uncertainty}"

def ljust_column(column):
    """
    Left justify the given list of strings to all have the same length.
    They will all share their maximum length.
    Return a new list of the modified strings.
    """
    max_length = max(len(cell) for cell in column)
    new_column = [cell.ljust(max_length) for cell in column]
    return new_column

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
        measurement_str = get_measurement_str(float(value), float(uncertainty), separator)
        column.append(measurement_str)
    column = ljust_column(column)
    if bar_after_header:
        max_length = len(column[0])
        bar = "-" * max_length
        column.insert(1, bar)
    return column

def get_trial_column(length, bar_after_header=True):
    """
    Get a list of left justified strings for the trial column.
    This column has 'Trial' as the header and simply counts off the rows.
    """
    column = ["Trial"]
    for i in range(length):
        column.append(str(i + 1))
    column = ljust_column(column)
    if bar_after_header:
        column.insert(1, "-" * len(column[0]))
    return column

def get_item_list(instructions, symbols=None):
    """
    Return the items specified by the given symbols in a list.
    If items=None, return a list of all the input and output items.
    """
    item_list = []
    if symbols == None:
        sections = ["inputs", "outputs"]
        for section in sections:
            for item in instructions[section]:
                item_list.append(item)
    else:
        for symbol in symbols:
            item = get_item(instructions, symbol)
            item_list.append(item)
    return item_list

def get_table_str(item_list, table_format):
    """
    Turn the given item list into a table with the specified table format (markdown|latex)
    """
    if table_format == "markdown":
        header_format = "{symbol} ({units})"
        col_separator = " | "
        pm_separator = "±"
        bar_after_header = True
    elif table_format == "latex":
        header_format = "\\mch{{${symbol}$ ({units})}}"
        col_separator = " & "
        pm_separator = "&"
        bar_after_header = False
    column_list = [item_to_column(item, header_format, pm_separator, bar_after_header) for item in item_list]
    trial_count = len(item_list[0]["value"])
    column_list.insert(0, get_trial_column(trial_count, bar_after_header))
    row_list = [[column[i] for column in column_list] for i in range(len(column_list[0]))]
    row_strs = [col_separator.join(row) for row in row_list]
    if table_format == "markdown":
        table_str = "\n".join(row_strs)
        return table_str
    if table_format == "latex":
        row_strs = [row + r" \\" for row in row_strs]
        row_strs = [row.replace(" -", "\\-") for row in row_strs]
        row_strs = [row.replace(".", "&") for row in row_strs]
        row_strs.insert(1, "\\mr")
        opening = "\\begin{table}[htbp]\n\caption{\label{}\n}\n"
        opening += "\\begin{indented}\\lineup\\item[]\\begin{tabular}{@{}l"
        item_count = len(item_list)
        opening += "\\mcm" * item_count 
        opening += "}\n\\br\n"
        closing = "\n\\br\n\\end{tabular}\\end{indented}\\end{table}"
        table_str = "\n".join(row_strs)
        return opening + table_str + closing

def print_results(instructions, table_format):
    """
    Based on a processed instructions object, print out the specified tables
    Use the desired table format (markdown|latex).
    
    For the LaTeX format assume these macros exist, among the other ones provided by the iopart class
    - \\def\\mcm{r@{.}l@{ ± }r@{.}l}
    - \\def\\mch#1{\multicolumn{4}{l}{#1}} 
    """
    desired_table_list = instructions["tables"]
    if len(desired_table_list) == 0:
        desired_table_list = [None]
    for desired_table in desired_table_list:
        item_list = get_item_list(instructions, desired_table)
        print(get_table_str(item_list, table_format))
        print()