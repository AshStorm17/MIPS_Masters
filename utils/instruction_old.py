class Instruction:
    def __init__(self, type, instruction):
        self.type = type
        self.fields = self.parse_instruction(instruction)
        self.__set_attributes()

    def parse_instruction(self, inst):
        # Create a dictionary to hold instruction fields
        fields = {
            'op': inst[0:6],          # All types
            'rs': inst[6:11],         # R-type and I-type
            'rt': inst[11:16],        # R-type and I-type
            'rd': inst[16:21],        # R-type
            'shamt': inst[21:26],     # R-type
            'funct': inst[26:32],     # R-type
            'immediate': inst[16:32],  # I-type
            'address': inst[6:32]      # J-type
        }
            
        return fields

    def __set_attributes(self):
        """Set the fields as attributes of the class for easy access."""
        for key, value in self.fields.items():
            setattr(self, key, value)

    def get_fields(self):
        """Return a dictionary of instruction fields and their values."""
        return self.fields

    def __str__(self):
        """Return a string representation of the instruction."""
        type_names = {0: 'R-type', 1: 'I-type', 2: 'J-type'}
        return f"{type_names[self.type]} Instruction: {self.fields}"

# Example usage
def test_instruction_parser():
    # Test R-type instruction
    r_type = "00000000001000100001100000100000"  # add $3, $1, $2
    r_inst = Instruction(0, r_type)
    print(r_inst)

    # Test I-type instruction
    i_type = "10001100001000100000000000000100"  # lw $2, 4($1)
    i_inst = Instruction(1, i_type)
    print(i_inst)

    # Test J-type instruction
    j_type = "00001000000000000000000000000100"  # j 4
    j_inst = Instruction(2, j_type)
    print(j_inst)

if __name__ == "__main__":
    test_instruction_parser()

# ---------------------------------------------------------

if __name__ == "__main__":
    inst = "00000001001010101000000000100010"  # R-type example
    instruction = Instruction(type=0, instruction=inst)
    print(instruction)  # Print string representation of the instruction
    fields_dict = instruction.get_fields()  # Get the fields as a dictionary
    print("Fields dictionary:", fields_dict)  # Print the fields dictionary
