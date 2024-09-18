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
                pass
            case 2|3:
                # handle J-type inst (pseudodirect addressing, updating PC)
                pass
            case _:
                # handle I-type inst (e.g. load, store, branch)
                pass

# -------------------------------------------------------