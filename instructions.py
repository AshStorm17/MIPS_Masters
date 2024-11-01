class Instruction:
    def __init__(self,type,instruction) :
        self.type=type
        self.fields=self.parse_instruction(instruction)
        self._set_attributes()
    def parse_instruction(self,inst):
        # Always get opcode
        fields = {'op': inst[0:6]}
        
        # R-type fields (type 0)
        fields['rs'] = inst[6:11]
        fields['rt'] = inst[11:16]
        fields['rd'] = inst[16:21]
        fields['shamt'] = inst[21:26]
        fields['funct'] = inst[26:32]
        
        # I-type fields (type 1)
        fields['immediate'] = inst[16:32]
        
        # J-type fields (type 2)
        fields['address'] = inst[6:32]
        
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