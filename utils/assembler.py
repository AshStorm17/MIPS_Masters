class MIPSAssembler:
    def __init__(self):
        # Instruction type formats
        self.r_format = {
            'add': '100000', 'sub': '100010', 'and': '100100', 'or': '100101', 'slt': '101010', 'nor': '100111',
            'sll': '000000', 'srl': '000010', 'sra': '000011', 'sltu': '101011', 'div': '011010', 'mult': '011000',
            'jr': '001000', 'xor': '100110', 'nor': '100111', 'mfhi': '010000', 'mflo': '010010', 'mthi': '010001', 'mtlo': '010011'
        }
        
        self.i_format = {
            'addi': '001000', 'andi': '001100', 'ori': '001101', 'beq': '000100', 'bne': '000101', 'lw': '100011',
            'sw': '101011', 'slti': '001010', 'xori': '001110', 'lui': '001111', 'sltiu': '001011', 'bgez': '000001',
            'bgtz': '000111', 'blez': '000110', 'bltz': '000001', 
            'lh': '100001', 'lhu': '100101', 'lb': '100000', 'lbu': '100100', 
            'sh': '101001', 'sb': '101000', 'syscall': '000000'  # Syscall opcode
        }
        
        self.j_format = {'j': '000010', 'jal': '000011'}
        
        # Register mappings
        self.registers = {
            '$0': '00000', '$at': '00001', '$v0': '00010', '$v1': '00011', '$a0': '00100', '$a1': '00101', '$a2': '00110', '$a3': '00111',
            '$t0': '01000', '$t1': '01001', '$t2': '01010', '$t3': '01011', '$t4': '01100', '$t5': '01101', '$t6': '01110', '$t7': '01111',
            '$s0': '10000', '$s1': '10001', '$s2': '10010', '$s3': '10011', '$s4': '10100', '$s5': '10101', '$s6': '10110', '$s7': '10111',
            '$t8': '11000', '$t9': '11001', '$k0':'11010','$k1':'11011', '$gp': '11100', '$sp': '11101', '$fp': '11110', '$ra': '11111'
        }

    def decimal_to_binary(self, value, bits):
        """Convert decimal or hexadecimal string to binary with specified number of bits"""
        if isinstance(value, str):
            if value.startswith('0x') or value.startswith('0X'):  # If value is hex
                decimal = int(value, 16)
            else:  # If value is decimal
                decimal = int(value)
        else:
            decimal = value

        if decimal < 0:
            # Handle negative numbers using 2's complement
            decimal = (1 << bits) + decimal
        binary = bin(decimal)[2:].zfill(bits)
        return binary[-bits:]

    def parse_instruction(self, instruction, labels,inst_line_num):
        """Parse MIPS instruction into components and resolve labels"""
        instruction = instruction.split('#')[0].strip()
        parts = instruction.replace(',', '').split()
        op = parts[0].lower()
        operands = parts[1:]

        # Check if the last operand is a label and replace it with the resolved address/offset
        if operands and operands[-1] in labels:
            operands[-1] = str(labels[operands[-1]]-inst_line_num)  # Resolve label to its corresponding address or offset
        return op, operands

    def resolve_labels(self, instructions):
        """First pass: Resolve label addresses in the instruction list"""
        labels = {}
        resolved_instructions = []
        line_number = 0

        # Identify labels and store their line numbers
        for instruction in instructions:
            if ':' in instruction:  # It's a label
                label = instruction.split(':')[0].strip()
                labels[label] = line_number
                continue  # Skip the label itself, don't add it as an instruction
            else:
                resolved_instructions.append(instruction)
                line_number += 1

        # Second pass: Replace labels with their resolved addresses
        for i, instruction in enumerate(resolved_instructions):
            op, operands = self.parse_instruction(instruction, labels,i+1)
            resolved_instructions[i] = f"{op} " + ", ".join(operands)
        
        return resolved_instructions, labels
    
    def check_register_validity(self, reg):
        """Ensure register is valid and $0 is not changed"""
        if reg not in self.registers:
            raise ValueError(f"Invalid register: {reg}")
        if reg == '$0':
            raise ValueError("Cannot modify $0 register (zero register)")

    def assemble_r_format(self, op, operands):
        """Convert R-format instruction to machine code"""
        opcode = '000000'
        
        if op in ['sll', 'srl', 'sra']:
            rd, rt, shamt = operands[0], operands[1], int(operands[2])
            self.check_register_validity(rd)
            self.check_register_validity(rt)
            machine_code = opcode + '00000' + self.registers[rt] + self.registers[rd] + self.decimal_to_binary(shamt, 5) + self.r_format[op]
        elif op == 'jr':
            rs = operands[0]
            self.check_register_validity(rs)
            machine_code = opcode + self.registers[rs] + '000000000000000' + self.r_format[op]
        else:
            rd, rs, rt = operands[0], operands[1], operands[2]
            self.check_register_validity(rd)
            self.check_register_validity(rs)
            self.check_register_validity(rt)
            machine_code = opcode + self.registers[rs] + self.registers[rt] + self.registers[rd] + '00000' + self.r_format[op]
        
        return machine_code

    def assemble_i_format(self, op, operands):
        """Convert I-format instruction to machine code"""
        opcode = self.i_format[op]
        
        if op in ['lw', 'sw', 'lh', 'lhu', 'lb', 'lbu', 'sh', 'sb']:
            rt, offset_base = operands[0], operands[1]
            offset, base = offset_base.split('(')
            base = base.rstrip(')')
            self.check_register_validity(rt)
            self.check_register_validity(base)
            machine_code = opcode + self.registers[base] + self.registers[rt] + self.decimal_to_binary(offset, 16)
        elif op in ['bgez', 'bgtz', 'blez', 'bltz']:
            rs, immediate = operands[0], operands[1]
            self.check_register_validity(rs)
            machine_code = opcode + self.registers[rs] + '00000' + self.decimal_to_binary(immediate, 16)
        else:
            rt, rs, immediate = operands[0], operands[1], operands[2]
            self.check_register_validity(rt)
            self.check_register_validity(rs)
            machine_code = opcode + self.registers[rs] + self.registers[rt] + self.decimal_to_binary(immediate, 16)
        
        return machine_code

    def assemble_j_format(self, op, operands):
        """Convert J-format instruction to machine code"""
        opcode = self.j_format[op]
        address = self.decimal_to_binary(int(operands[0]), 26)
        return opcode + address

    def assemble_syscall(self):
        """Convert syscall to machine code"""
        return '00000000000000000000000000001100'  # Syscall in R-format with funct code 0xC

    def assemble_binary(self, instructions):
        """Convert MIPS instructions to binary machine code"""
        instructions, labels = self.resolve_labels(instructions)
        binary_codes = []
        for instruction in instructions:
            op, operands = self.parse_instruction(instruction, labels)
            if op == 'syscall':
                binary = self.assemble_syscall()
            elif op in self.r_format:
                binary = self.assemble_r_format(op, operands)
            elif op in self.i_format:
                binary = self.assemble_i_format(op, operands)
            elif op in self.j_format:
                binary = self.assemble_j_format(op, operands)
            else:
                raise ValueError(f"Unknown instruction: {op}")
            
            binary_codes.append(binary)
        
        return binary_codes

    def format_machine_codes(self, binary_codes):
        """Convert binary codes to hexadecimal format and format as string"""
        formatted_codes = [f"0x{hex(int(binary, 2))[2:].zfill(8)} => {binary}" for binary in binary_codes]
        return formatted_codes

    def parse_asm(self, file_path):
        instructions = []
        with open(file_path, 'r') as file:
            for line in file:
                # Strip whitespace and ignore empty lines or comments
                line = line.strip()
                if line and not line.startswith('#'):  # Exclude comments if any
                    instructions.append(line)
        return instructions

def main():
    assembler = MIPSAssembler()
    
    # Replace with the path to your assembly code file
    test_instructions = assembler.parse_asm("../assets/tests/lh_lbu_test.asm")

    print("MIPS Assembly to Machine Code Conversion:")
    print("-" * 60)
    print(f"{'Instruction':<25} {'Hex':<12} Binary")
    print("-" * 60)

    machine_codes = assembler.assemble_binary(test_instructions)
    format_code = assembler.format_machine_codes(machine_codes)
    
    save=True
    if (save):
        #write machine code to text file
        file_path="../assets/tests/lh_lbu_test.txt"
        with open(file_path, 'w') as file:
                for code in machine_codes:
                    file.write(f"{code}\n")
        print(f"\nMachine code successfully written to {file_path}")

    for code in format_code:
        print(code)

def check_resolve_inst():
    assembler = MIPSAssembler()
    
    # Replace with the path to your assembly code file
    test_instructions = assembler.parse_asm("assets\mipsasm_1.asm")
    instructions, labels = assembler.resolve_labels(test_instructions)
    print(instructions,'------------',labels)

if __name__ == "__main__":
    # main()
    check_resolve_inst()
