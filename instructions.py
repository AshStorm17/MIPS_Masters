# Instruction Formats---------------------------------------
class RtypeInst:
    def __init__(self, op, rs, rt, rd, shamt, funct):
        self.type = 0
        self.op = op
        self.rs = rs       
        self.rt = rt       
        self.rd = rd       
        self.shamt = shamt 
        self.funct = funct 

# ---------------------------
class ItypeInst:
    def __init__(self, op, rs, rt, addrORimm):
        self.type = 1
        self.op = op
        self.rs = rs
        self.rt = rt
        self.addrORimm = addrORimm

    def relativeAddr(self, PC):
        pass
        
# ---------------------------

class JtypeInst:
    def __init__(self, op, address):
        self.type = 2
        self.op = op
        self.address = address

    def jumpAddr(self, PC): 
        PC_plus_4 = int(PC,2) + 4               # PC + 4
        PC4 = format(PC_plus_4, '032b')         # returns 32-bit (unsigned) binary string
        return PC4[0:4] + self.address + "00"   # pseudodirect addressing

# ---------------------------------------------------------
def giveFields(inst, type):
    opcode = inst[0:6]  
    fields = [opcode]   
    match type:
        case 0:
            rs = inst[6:11]         
            rt = inst[11:16]
            rd = inst[16:21]
            shamt = int[21:26]
            funct = inst[26:32]
            fields.extend(rs,rt,rd,shamt,funct)

        case 1:
            rs = inst[6:11]         
            rt = inst[11:16]
            addrORimm = inst[16:32]
            fields.extend(rs,rt,addrORimm)
        case 2:
            address = inst[6:32]
            fields.extend(address)
    return fields

# ---------------------------------------------------------
