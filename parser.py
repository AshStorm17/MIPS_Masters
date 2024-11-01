class MIPSParser:
    def __init__(self, memory):
        self.memory = memory

    def parse_r_type(self, instruction):
        opcode = (instruction >> 26) & 0x3F
        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F
        rd = (instruction >> 11) & 0x1F
        shamt = (instruction >> 6) & 0x1F
        funct = instruction & 0x3F
        return f"R-type: opcode={opcode:02x}, rs={rs:02x}, rt={rt:02x}, rd={rd:02x}, shamt={shamt:02x}, funct={funct:02x}"

    def parse_i_type(self, instruction):
        opcode = (instruction >> 26) & 0x3F
        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F
        immediate = instruction & 0xFFFF
        return f"I-type: opcode={opcode:02x}, rs={rs:02x}, rt={rt:02x}, immediate={immediate:04x}"

    def parse_j_type(self, instruction):
        opcode = (instruction >> 26) & 0x3F
        address = instruction & 0x3FFFFFF
        return f"J-type: opcode={opcode:02x}, address={address:07x}"

    def parse_instruction(self, instruction):
        opcode = (instruction >> 26) & 0x3F
        if opcode == 0:
            return self.parse_r_type(instruction)
        elif opcode in [2, 3]:
            return self.parse_j_type(instruction)
        else:
            return self.parse_i_type(instruction)

    def parse_mips_file(self, file_path):
        addr = 0
        parsed_instructions = []  # List to hold the parsed instructions
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    instruction = line.strip()
                    if len(instruction) == 32 and all(bit in '01' for bit in instruction):
                        # Convert binary string to an integer
                        instruction_int = int(instruction, 2)
                        self.memory.store(addr, instruction)
                        parsed_instruction = self.parse_instruction(instruction_int)
                        parsed_instructions.append(parsed_instruction)
                        addr += 4
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

        return parsed_instructions

    def test_parser(self, file_path):
        """Test the parser with the given file path."""
        parsed_instrs = self.parse_mips_file(file_path)
        for instr in parsed_instrs:
            print(instr)
