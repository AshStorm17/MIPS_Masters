from components.memory import Memory

class MIPSParser:
    def __init__(self):
        self.memory = Memory()

    def parse_r_type(self, instruction):
        return {
            "opcode": (instruction >> 26) & 0x3F,
            "rs": (instruction >> 21) & 0x1F,
            "rt": (instruction >> 16) & 0x1F,
            "rd": (instruction >> 11) & 0x1F,
            "shamt": (instruction >> 6) & 0x1F,
            "funct": instruction & 0x3F
        }

    def parse_i_type(self, instruction):
        return {
            "opcode": (instruction >> 26) & 0x3F,
            "rs": (instruction >> 21) & 0x1F,
            "rt": (instruction >> 16) & 0x1F,
            "immediate": instruction & 0xFFFF
        }

    def parse_j_type(self, instruction):
        return {
            "opcode": (instruction >> 26) & 0x3F,
            "address": instruction & 0x3FFFFFF
        }

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
        parsed_instructions = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    instruction = line.strip()
                    if len(instruction) == 32 and all(bit in '01' for bit in instruction):
                        # Store the binary string directly as IR
                        self.memory.store(addr, instruction)
                        parsed_instructions.append({
                            "PC": addr,
                            "IR": instruction
                        })
                        addr += 4
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

        return parsed_instructions

    def test_parser(self, file_path):
        """Test the parser with the given file path."""
        parsed_instructions = self.parse_mips_file(file_path)
        print("Parsed instructions:", parsed_instructions)


if __name__ == "__main__":
    mips_parser = MIPSParser()
    mips_parser.test_parser("assets/binary.txt")
