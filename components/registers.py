# --------------------------------------------
class Registers:
    def __init__(self):
        self.reg = [""] * 32 # 32 registers

    def write(self, number, value):
        self.reg[number] = value
    
    def read(self, number):
        return self.reg[number]
    
    def reset(self):
        self.reg = [""] * 32

    def get_registers(self):
        return self.reg
    
    def __getitem__(self, key):
        return self.reg[key]
    
    def __setitem__(self, key, value):
        self.reg[key] = value

# --------------------------------------------
