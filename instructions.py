class Instruction:
    def __init__(self, type, instruction):
        self.type = type
        self.fields = self.parse_instruction(instruction)

    def parse_instruction(self, inst):
        # Create a dictionary to hold instruction fields
        fields = {'op': inst[0:6]}  # Always include opcode

        # R-type fields (type 0)
        if self.type == 0:
            fields['rs'] = inst[6:11]
            fields['rt'] = inst[11:16]
            fields['rd'] = inst[16:21]
            fields['shamt'] = inst[21:26]
            fields['funct'] = inst[26:32]

        # I-type fields (type 1)
        elif self.type == 1:
            fields['rs'] = inst[6:11]
            fields['rt'] = inst[11:16]
            fields['immediate'] = inst[16:32]  # immediate is the last 16 bits

        # J-type fields (type 2)
        elif self.type == 2:
            fields['address'] = inst[6:32]  # address is the last 26 bits

        return fields

    def get_fields(self):
        """Return a dictionary of instruction fields and their values."""
        return self.fields

    def __str__(self):
        """Return a string representation of the instruction."""
        type_names = {0: 'R-type', 1: 'I-type', 2: 'J-type'}
        return f"{type_names[self.type]} Instruction: {self.fields}"

# ---------------------------------------------------------

if __name__ == "__main__":
    inst = "00000001001010101000000000100010"  # R-type example
    instruction = Instruction(type=0, instruction=inst)
    print(instruction)  # Print string representation of the instruction
    fields_dict = instruction.get_fields()  # Get the fields as a dictionary
    print("Fields dictionary:", fields_dict)  # Print the fields dictionary
