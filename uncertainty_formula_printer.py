from sympy.parsing.sympy_parser import parse_expr
from sympy.printing.latex import latex

if __name__ == "__main__":
    # Get the symbol and formula input
    symbol = input("Please input a symbol\n>>> ")
    expr_str = input("Please input a formula\n>>> ")
    expr = parse_expr(expr_str)
    # Print the LaTeX string for the expression
    latex_str = f"{symbol} = {latex(expr)}"
    print(latex_str)
    # Print the partial derivative expression
    squared_partial_strs = [f"\\left(\\frac{{\\partial {symbol}}}{{\\partial {item}}} \Delta {item} \\right)^2" for item in expr.free_symbols]
    squared_partial_sum_str = f"\\Delta {symbol} = \\sqrt{{ {' + '.join(squared_partial_strs)} }}"
    print(squared_partial_sum_str)
    # Print the filled out partial derivative expression
    squared_partial_strs = []
    for item in expr.free_symbols:
        partial = expr.diff(item)
        partial_str = latex(partial)
        squared_partial_str = f"({partial_str} \Delta {item})^2"
        squared_partial_strs.append(squared_partial_str)
    squared_partial_sum_str = f"\\Delta {symbol} = \\sqrt{{ {' + '.join(squared_partial_strs)} }}"
    print(squared_partial_sum_str)
    