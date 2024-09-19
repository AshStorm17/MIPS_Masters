def hex_to_binary(hex_string):
    # Remove '0x' prefix if present
    hex_string = hex_string.lower().replace('0x', '')
    
    # Dictionary to map hex digits to 4-bit binary strings
    hex_to_bin = {
        '0': '0000', '1': '0001', '2': '0010', '3': '0011',
        '4': '0100', '5': '0101', '6': '0110', '7': '0111',
        '8': '1000', '9': '1001', 'a': '1010', 'b': '1011',
        'c': '1100', 'd': '1101', 'e': '1110', 'f': '1111'
    }
    
    return ''.join(hex_to_bin[char] for char in hex_string)

def binary_to_hex(binary_string):
    # Ensure the binary string length is a multiple of 4
    binary_string = binary_string.zfill((len(binary_string) + 3) // 4 * 4)
    
    # Dictionary to map 4-bit binary strings to hex digits
    bin_to_hex = {
        '0000': '0', '0001': '1', '0010': '2', '0011': '3',
        '0100': '4', '0101': '5', '0110': '6', '0111': '7',
        '1000': '8', '1001': '9', '1010': 'a', '1011': 'b',
        '1100': 'c', '1101': 'd', '1110': 'e', '1111': 'f'
    }
    
    hex_result = ''
    for i in range(0, len(binary_string), 4):
        hex_result += bin_to_hex[binary_string[i:i+4]]
    
    return hex_result

def parse_hex_file(file_path):
    binary_instructions = []

    try:
        # Open the hex file
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                hex_instruction = line.strip()  # Remove any surrounding whitespace
                if hex_instruction:  # Check if line is not empty
                    binary_instruction = hex_to_binary(hex_instruction)
                    binary_instructions.append(binary_instruction)

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return binary_instructions

def write_binary_to_file(binary_instructions, output_file_path):
    try:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            for binary_instruction in binary_instructions:
                file.write(binary_instruction + '\n')
        print(f"Binary instructions written to '{output_file_path}' successfully.")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")


# Example usage
if __name__=="__main__":
    print(hex_to_binary('2408001e'))  # Output: 0001101000111111
    print(binary_to_hex('0001101000111111'))  # Output: 1a3f

    ptmp=parse_hex_file("assets\hex.txt")
    print(ptmp)
    write_binary_to_file(ptmp,"assets\\binary.txt")