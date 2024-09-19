class Execute:
    def __init__(self, memory, registers, alu):
        self.memory = memory
        self.registers = registers
        self.alu = alu

    # execute the sent instruction (inst object)
    def executeInst(self, inst):
        match inst.type:
            case 0:
                # handle R-type inst (e.g. using ALU)
                # op, rs, rt, rd, shamt, funct
                """
                    nor,            (nor=100111) 
                    sll, srl,       (sll=000000, srl=000010)
                    sltu,           (sltu=101011)
                    jr              (jr=001000)
                """
                if inst.rs == 0:
                    opr1 = self.registers.reg[inst.rt]
                    ans = self.alu.alu_shift(inst.funct, opr1, inst.shamt)
                    self.registers.reg[inst.rd] = ans
                else:
                    opr1 = self.registers.reg[inst.rs]
                    opr2 = self.registers.reg[inst.rt]
                    ans = self.alu.alu_arith(inst.funct, opr1, opr2)

                pass
            case 2|3:
                # handle J-type inst 
                """
                    j, jal (pseudodirect addressing, updating PC)
                """
                pass
            case _:
                # handle I-type inst
                """
                    addi,
                    beq, bne,
                    slti, sltiu
                    lw, sw,
                    lh, lhu,
                    lb, lbu,
                    sh, sb,
                    lui, 
                    ori, andi,
                """
                pass

# -------------------------------------------------------
