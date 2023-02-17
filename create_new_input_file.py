def get_input_list():
    """
    Get a list of input strings from the user.
    Stop collecting strings if an input is blank.
    """
    input_list = []
    while True:
        input_str = input(">>> ")
        if input_str:
            input_list.append(input_str)
        else:
            break
    return input_list

categories = ["constants", "inputs", "outputs"]

constant_item = """
    {{
      "symbol": "{symbol}",
      "value": 0,
      "uncertainty": 0,
      "units": ""
    }}"""

input_item = """
    {{
      "symbol": "{symbol}",
      "value": [
        0
      ],
      "uncertainty": "",
      "units": ""
    }}"""

output_item = """
    {{
      "symbol": "{symbol}",
      "value": "",
      "units": ""
    }}"""

item_templates = [constant_item, input_item, output_item]

file_template = """{{
  "constants": [{}
  ],
  "inputs": [{}
  ],
  "outputs": [{}
  ],
  "tables": [
    
  ]
}}"""

if __name__ == "__main__":
    file_location = input("Where would you like to save this new input file?\n>>> ")
    msg = "List the symbols for the {}:"
    
    symbol_lists = []
    for category in categories:
        print(msg.format(category))
        symbols = get_input_list()
        symbol_lists.append(symbols)
    
    replacements = []
    for symbols, template in zip(symbol_lists, item_templates):
        item_str_list = []
        for symbol in symbols:
            item_str = template.format(symbol=symbol)
            item_str_list.append(item_str)
        replacements.append(",".join(item_str_list))
    
    result = file_template.format(*replacements)
    print(result)
    
    if file_location:
       with open(file_location, mode="w", encoding="utf-8") as f:
           f.write(result)
