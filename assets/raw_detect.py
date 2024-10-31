def detect_raw_hazard(instructions):
    """
    Detects RAW (Read After Write) hazards in a given set of MIPS instructions.
    
    Args:
        instructions (list): A list of MIPS assembly instructions.
        
    Returns:
        list: A list of tuples, where each tuple represents a RAW hazard and contains:
              (instruction_idx, register, dependent_instruction_idx)
    """
    register_write_history = {
        "$zero": [],
        "$at": [],
        "$v0": [],
        "$v1": [],
        "$a0": [],
        "$a1": [],
        "$a2": [],
        "$a3": [],
        "$t0": [],
        "$t1": [],
        "$t2": [],
        "$t3": [],
        "$t4": [],
        "$t5": [],
        "$t6": [],
        "$t7": [],
        "$s0": [],
        "$s1": [],
        "$s2": [],
        "$s3": [],
        "$s4": [],
        "$s5": [],
        "$s6": [],
        "$s7": [],
        "$t8": [],
        "$t9": [],
        "$k0": [],
        "$k1": [],
        "$gp": [],
        "$sp": [],
        "$fp": [],
        "$ra": []
    }

    raw_hazards = []

    for i, instruction in enumerate(instructions):
        instruction_parts = instruction.split()
        opcode = instruction_parts[0]

        if opcode in ["add", "sub", "and", "or", "nor", "slt", "sltu"]:
            reg_dst = instruction_parts[1]
            reg_src1 = instruction_parts[2]
            reg_src2 = instruction_parts[3]

            # Check for RAW hazards
            for j in range(i-1, -1, -1):
                if reg_src1 in instructions[j]:
                    if j not in register_write_history[reg_src1]:
                        raw_hazards.append((j, reg_src1, i))
                        break
                if reg_src2 in instructions[j]:
                    if j not in register_write_history[reg_src2]:
                        raw_hazards.append((j, reg_src2, i))
                        break

            # Update the write history
            register_write_history[reg_dst].append(i)

        elif opcode in ["addi", "andi", "ori", "slti", "sltiu"]:
            reg_dst = instruction_parts[1]
            reg_src = instruction_parts[2]

            # Check for RAW hazards
            for j in range(i-1, -1, -1):
                if reg_src in instructions[j]:
                    if j not in register_write_history[reg_src]:
                        raw_hazards.append((j, reg_src, i))
                        break

            # Update the write history
            register_write_history[reg_dst].append(i)

        elif opcode in ["lw", "lh", "lhu", "lb", "lbu"]:
            reg_dst = instruction_parts[1]
            reg_src = instruction_parts[2].split("(")[1][:-1]

            # Check for RAW hazards
            for j in range(i-1, -1, -1):
                if reg_src in instructions[j]:
                    if j not in register_write_history[reg_src]:
                        raw_hazards.append((j, reg_src, i))
                        break

            # Update the write history
            register_write_history[reg_dst].append(i)

        elif opcode in ["sw", "sh", "sb"]:
            reg_src = instruction_parts[1]
            reg_dst = instruction_parts[2].split("(")[1][:-1]

            # Check for RAW hazards
            for j in range(i-1, -1, -1):
                if reg_dst in instructions[j]:
                    if j not in register_write_history[reg_dst]:
                        raw_hazards.append((j, reg_dst, i))
                        break
            for j in range(i-1, -1, -1):
                if reg_src in instructions[j]:
                    if j not in register_write_history[reg_src]:
                        raw_hazards.append((j, reg_src, i))
                        break

            # Update the write history
            register_write_history[reg_dst].append(i)
            register_write_history[reg_src].append(i)

    return raw_hazards

if __name__=="__main__":
    instructions = [
    "add $t0 $s1 $s2",
    "sub $t1 $t0 $s3",
    "lw $t2 8($s1)",
    "add $t3 $t1 $t2"
]

    raw_hazards = detect_raw_hazard(instructions)
    print(raw_hazards)