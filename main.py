import sys
from instruction_loader import load_instructions
from instruction_processor import process_instructions
from result_printer import print_results

if __name__ == "__main__":
    file_name = sys.argv[1]
    # Default the table_format to "markdown"
    if len(sys.argv) == 3:
        table_format = sys.argv[2]
    else:
        table_format = "markdown"
    
    instructions = load_instructions(file_name)
    process_instructions(instructions)
    print_results(instructions, table_format)
