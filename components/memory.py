# --------------------------------------------
# Memory class
    # byte addressing
    # separate spaces for instructions, data, I/O
class Memory:
    def __init__(self):
        self.data = [""]*4*1024 # 1024 words

    def store(self, addr, value):
        self.data[addr]=value[:8]
        self.data[addr+1]=value[8:16]
        self.data[addr+2]=value[16:24]
        self.data[addr+3]=value[24:32]

    def load(self, addr):
        return self.data[addr]
    
    # function for I/O access
    def fillOutput(self):
        pass

    def clear_data(self):
        self.data = [""]*4*1024

    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value

# -------------------------------------------
