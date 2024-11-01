# --------------------------------------------
class Registers:
    def __init__(self, initialise=False):
        self.reg = [""] * 32 # 32 registers

        self.reg[0] = format(0, '032b')     # $zero register
        self.reg[31] = format(0, '032b')    # $ra = 0 (default = exit main())
        self.reg[29] = format(1024, '032b') # $sp = 4092 (default pointing to top address in the memory)
        self.reg[30] = format(1024, '032b') # $fp = 4092 (default pointing to top address in the memory)

        # uninitialised: global pointer, argument regs, value regs

        if initialise==True:
            for i in range(8,26):
                self.reg[i] = "0"*32 # initialise s0-s7 and temporaries with 0's
            self.reg[16] = format(5, '032b')    # $s0 = 5
            self.reg[17] = format(10, '032b')   # $s1 = 10
            self.reg[18] = format(1, '032b')    # $s2 = 1

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
