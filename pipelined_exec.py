class Execute:
    def __init__(self, memory, registers, alu):
        self.memory = memory
        self.registers = registers
        self.alu = alu

    # Stage 3: Execute (EX) - Performs ALU operations
    def execute(self, ID_EX, EX_MEM):
        inst_type = ID_EX['inst_type']
        fields = ID_EX['fields']
        
        match inst_type:
            case RtypeInst:
                # Handle R-type instruction
                src_reg = int(fields.rs, 2)
                temp_reg = int(fields.rt, 2)

                if fields.funct == "001000":  # `jr` instruction
                    EX_MEM['PC'] = self.registers.read(src_reg)
                elif fields.funct.startswith("000"):
                    opr1 = self.registers.read(src_reg)
                    EX_MEM['ALU_result'] = self.alu.alu_shift(fields.funct, opr1, fields.shamt)
                else:
                    opr1 = self.registers.read(src_reg)
                    opr2 = self.registers.read(temp_reg)
                    EX_MEM['ALU_result'] = self.alu.alu_arith(fields.funct, opr1, opr2)
                
                EX_MEM['dest_reg'] = int(fields.rd, 2)
                EX_MEM['inst_type'] = inst_type

            case JtypeInst:
                # Handle J-type instruction (j, jal)
                addr = int(fields.address, 2)
                if int(fields.op[3:], 2) == 2:  # jump
                    EX_MEM['PC'] = (ID_EX['PC'] & 0xF0000000) | (addr << 2)
                else:  # jump and link
                    self.registers.write(31, ID_EX['PC'] + 4)  # write return address
                    EX_MEM['PC'] = (ID_EX['PC'] & 0xF0000000) | (addr << 2)

            case ItypeInst:
                # Handle I-type instruction (load/store, branch, immediate arithmetic)
                match fields.op[0:3]:
                    case "100":  # Load instruction
                        addr = int(self.alu.giveAddr(fields.rs, fields.addrORimm), 2)
                        EX_MEM['mem_addr'] = addr
                        EX_MEM['dest_reg'] = int(fields.rt, 2)
                        EX_MEM['inst_type'] = "load"

                    case "101":  # Store instruction
                        addr = int(self.alu.giveAddr(fields.rs, fields.addrORimm), 2)
                        EX_MEM['mem_addr'] = addr
                        EX_MEM['src_data'] = self.registers.read(int(fields.rt, 2))
                        EX_MEM['inst_type'] = "store"

                    case "001":  # Immediate arithmetic
                        src = self.registers.read(int(fields.rs, 2))
                        EX_MEM['ALU_result'] = self.alu.alu_arith_i(fields.op[3:6], src, fields.addrORimm)
                        EX_MEM['dest_reg'] = int(fields.rt, 2)
                        EX_MEM['inst_type'] = "arith_i"

                    case "000":  # Branching (beq, bne)
                        src_val = self.registers.read(int(fields.rs, 2))
                        dst_val = self.registers.read(int(fields.rt, 2))
                        imm = int(fields.addrORimm, 2)
                        if imm & 0x8000:  # sign-extend if negative
                            imm |= 0xFFFF0000
                        equal = self.alu.isEqual(src_val, dst_val)
                        branch_condition = int(fields.op[3:], 2) == 4  # beq if 4, bne otherwise
                        if equal == branch_condition:
                            EX_MEM['PC'] = ID_EX['PC'] + 4 + (imm << 2)
                        EX_MEM['inst_type'] = "branch"
