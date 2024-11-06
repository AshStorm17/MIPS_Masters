
def parse_r_type(instruction):
    opcode = (instruction >> 26) & 0x3F
    rs = (instruction >> 21) & 0x1F
    rt = (instruction >> 16) & 0x1F
    rd = (instruction >> 11) & 0x1F
    shamt = (instruction >> 6) & 0x1F
    funct = instruction & 0x3F
    return f"R-type: opcode={opcode:02x}, rs={rs:02x}, rt={rt:02x}, rd={rd:02x}, shamt={shamt:02x}, funct={funct:02x}"

def parse_i_type(instruction):
    opcode = (instruction >> 26) & 0x3F
    rs = (instruction >> 21) & 0x1F
    rt = (instruction >> 16) & 0x1F
    immediate = instruction & 0xFFFF
    return f"I-type: opcode={opcode:02x}, rs={rs:02x}, rt={rt:02x}, immediate={immediate:04x}"

def parse_j_type(instruction):
    opcode = (instruction >> 26) & 0x3F
    address = instruction & 0x3FFFFFF
    return f"J-type: opcode={opcode:02x}, address={address:07x}"

def parse_instruction(instruction):
    opcode = (instruction >> 26) & 0x3F
    if opcode == 0:
        return parse_r_type(instruction)
    elif opcode in [2, 3]:
        return parse_j_type(instruction)
    else:
        return parse_i_type(instruction)
    

def parse_mips_file(file_path,Memory):
    addr=0
    try:    
        with open(file_path,'r') as f:
            for line in f:
                instruction=line.strip()
                if len(instruction) == 32 and all(bit in '01' for bit in instruction):
                    Memory.store(addr,instruction)
                    addr+=4
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    


if __name__=="__main__":
    
    bin_instrs=parse_mips_file("assets\\binary.txt")
    print(bin_instrs)
            
