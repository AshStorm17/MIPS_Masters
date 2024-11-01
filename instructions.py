class Instruction:
    def __init__(self,type,instruction) :
        self.type=type
        self.fields=self.parse_instruction(instruction)
        self._set_attributes()
    def parse_instruction(self,inst):
         # Always get opcode
        fields = {'op': inst[0:6]}
        # Parse remaining fields based on instruction type
        if self.type == 0:    # R-type
            fields.update({
                'rs': inst[6:11],
                'rt': inst[11:16],
                'rd': inst[16:21],
                'shamt': inst[21:26],
                'funct': inst[26:32]
            })
        elif self.type == 1:  # I-type
            fields.update({
                'rs': inst[6:11],
                'rt': inst[11:16],
                'immediate': inst[16:32]
            })
        elif self.type == 2:  # J-type
            fields.update({
                'address': inst[6:32]
            })
        else:
            raise ValueError("Invalid instruction type. Must be 0 (R-type), 1 (I-type), or 2 (J-type)")
        
        return fields
    def _set_attributes(self):
        """Set the parsed fields as attributes of the class instance."""
        for field, value in self.fields.items():
            setattr(self, field, value)
    def __str__(self):
        """Return a string representation of the instruction."""
        type_names = {0: 'R-type', 1: 'I-type', 2: 'J-type'}
        fields_str = ', '.join(f'{k}={v}' for k, v in self.fields.items())
        return f"{type_names[self.type]} Instruction: {fields_str}"

# ---------------------------------------------------------

if __name__=="__main__":
    inst="00000001001010101000000000100010"
    inst=Instruction(type=0,instruction=inst)
    print(inst)
    print(inst.rt)