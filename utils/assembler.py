class MIPSAssembler:
    def __init__(self):
        # Instruction type formats
        self.r_format = {'add': '100000', 'sub': '100010', 'and': '100100', 
                        'or': '100101', 'slt': '101010', 'nor': '100111',
                        'sll': '000000', 'srl': '000010'}
        
        self.i_format = {'addi': '001000', 'andi': '001100', 'ori': '001101',
                        'beq': '000100', 'bne': '000101', 'lw': '100011',
                        'sw': '101011', 'slti': '001010'}
        
        self.j_format = {'j': '000010', 'jal': '000011'}
        
        # Register mappings
        self.registers = {
            '$zero': '00000', '$at': '00001',
            '$v0': '00010', '$v1': '00011',
            '$a0': '00100', '$a1': '00101', '$a2': '00110', '$a3': '00111',
            '$t0': '01000', '$t1': '01001', '$t2': '01010', '$t3': '01011',
            '$t4': '01100', '$t5': '01101', '$t6': '01110', '$t7': '01111',
            '$s0': '10000', '$s1': '10001', '$s2': '10010', '$s3': '10011',
            '$s4': '10100', '$s5': '10101', '$s6': '10110', '$s7': '10111',
            '$t8': '11000', '$t9': '11001', '$k0':'11010','$k1':'11011',
            '$gp': '11100', '$sp': '11101', '$fp': '11110', '$ra': '11111'
        }

    def decimal_to_binary(self, decimal, bits):
        """Convert decimal to binary with specified number of bits"""
        if decimal < 0:
            # Handle negative numbers using 2's complement
            decimal = (1 << bits) + decimal
        binary = bin(decimal)[2:].zfill(bits)
        return binary[-bits:]

    def parse_instruction(self, instruction):
        """Parse MIPS instruction into components"""
        parts = instruction.replace(',', '').split()
        op = parts[0].lower()
        operands = parts[1:]
        return op, operands

    def assemble_r_format(self, op, operands):
        """Convert R-format instruction to machine code"""
        opcode = '000000'
        
        if op in ['sll', 'srl']:
            rd = self.registers[operands[0]]
            rt = self.registers[operands[1]]
            shamt = self.decimal_to_binary(int(operands[2]), 5)
            rs = '00000'
        else:
            rd = self.registers[operands[0]]
            rs = self.registers[operands[1]]
            rt = self.registers[operands[2]]
            shamt = '00000'
        
        funct = self.r_format[op]
        machine_code = opcode + rs + rt + rd + shamt + funct
        return machine_code

    def assemble_i_format(self, op, operands):
        """Convert I-format instruction to machine code"""
        opcode = self.i_format[op]
        
        if op in ['lw', 'sw']:
            rt = self.registers[operands[0]]
            # Parse offset and base register from memory operand
            offset, base = operands[1].split('(')
            base = base.rstrip(')')
            rs = self.registers[base]
            immediate = self.decimal_to_binary(int(offset), 16)
        else:
            rt = self.registers[operands[0]]
            rs = self.registers[operands[1]]
            immediate = self.decimal_to_binary(int(operands[2]), 16)
        
        machine_code = opcode + rs + rt + immediate
        return machine_code

    def assemble_j_format(self, op, operands):
        """Convert J-format instruction to machine code"""
        opcode = self.j_format[op]
        address = self.decimal_to_binary(int(operands[0]), 26)
        machine_code = opcode + address
        return machine_code

    def assemble(self, instruction):
        """Convert MIPS instruction to machine code"""
        op, operands = self.parse_instruction(instruction)
        
        if op in self.r_format:
            binary = self.assemble_r_format(op, operands)
        elif op in self.i_format:
            binary = self.assemble_i_format(op, operands)
        elif op in self.j_format:
            binary = self.assemble_j_format(op, operands)
        else:
            raise ValueError(f"Unknown instruction: {op}")
        
        # Convert binary to hexadecimal
        hex_code = hex(int(binary, 2))[2:].zfill(8)
        return f"0x{hex_code}", binary

def parse_asm(file_path):
    instructions = []
    with open(file_path, 'r') as file:
        for line in file:
            # Strip whitespace and ignore empty lines or comments
            line = line.strip()
            if line and not line.startswith('#'):  # Exclude comments if any
                instructions.append(line)
    return instructions
# Example usage


def main():
    assembler = MIPSAssembler()
    
    # Test instructions
    test_instructions=parse_asm("assets\mipsasm.asm")

    # test_instructions = [
    #     "add $t1, $s1, $s2",
    #     "sll $t2, $t0, 2",
    #     "addi $s0, $t1, -3",
    #     "lw $t0, 4($s0)",
    #     "sw $t1, 8($s2)",
    #     "beq $t0, $t1, 16",
    #     "j 1000" 
    # ]
    


    print("MIPS Assembly to Machine Code Conversion:")
    print("-" * 60)
    print(f"{'Instruction':<25} {'Hex':<12} Binary")
    print("-" * 60)
    
    for instruction in test_instructions:
        try:
            hex_code, binary = assembler.assemble(instruction)
            print(f"{instruction:<25} {hex_code:<12} {binary}")
        except ValueError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()