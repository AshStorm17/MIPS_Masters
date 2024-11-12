class Memory:
    def __init__(self, initialise=False):
        self.data = [""]*4*1024 # 1024 words # byte addressing
        if initialise==True:
            self.data = [format(0, '008b')]*4*1024 # initialise with all 0's
            # test data filled for loading
            self.data[1000] = "11111011" 
            self.data[1001] = "00001111"
            self.data[1002] = "00000010"
            self.data[1003] = "00000001"
    def store(self, addr, value):
        
        self.data[addr]=value

    # loads a byte
    def load(self, addr):
        
        """ Check if addr is io_address, if yes, get the value as input from the user recieved via the application, store it in that location and return the same values. """
        return self.data[addr]
    
    def fillOutput(self, addr, wordData):
        """Memory mapped I/O"""
        # Reserve address 2000-2019 for display output (4 words for output)
        # Assumed: used only through store word instruction onto these words in the memory
        for i in range(4):
            self.data[addr+i] = wordData[i*8:(i+1)*8]

    def clear_data(self):
        self.data = [""]*4*1024

    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value

# -------------------------------------------
