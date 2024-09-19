# --------------------------------------------
# Memory class
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
    def fillOutput(self):
        pass

# -------------------------------------------
