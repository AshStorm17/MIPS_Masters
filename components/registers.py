# --------------------------------------------
class Registers:
    def __init__(self):
        self.reg = [""] * 32 # 32 registers

    def write(self, number, value):
        self.reg[number] = value
    
    def read(self, number):
        return self.reg[number]
# --------------------------------------------
