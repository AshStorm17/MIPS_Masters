# --------------------------------------------
# memory class
    # byte addressing
    # separate spaces for instructions, data, I/O
class Memory:
    def __init__(self):
        self.data = [""]*4*1024 # 1024 words

    def store(self, addr, value):
        self.data[addr] = value

    def load(self, addr):
        return self.data[addr]
    
    # function for I/O access

# --------------------------------------------
class ALU:
    def __init__(self):
        pass

    def execute(self, operation, opr1, opr2):
        pass


# --------------------------------------------
class Registers:
    def __init__(self):
        self.reg = [""] * 32 # 32 registers

    def write(self, number, value):
        self.reg[number] = value
    
    def read(self, number):
        return self.reg[number]
    

# --------------------------------------------