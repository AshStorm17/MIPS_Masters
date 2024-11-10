def signedVal(binStr):
    isSigned = int(binStr[0]=="1")
    return int(binStr, 2) - isSigned*(2**len(binStr))

def signedBin(num):
    # return 2's complement binary string of length 32
    ans=""  
    if(num<0):
        ans = bin(num % (1<<32))[2:]
    else:
        ans = format(num, '032b')
    return ans

class Registers:
    def __init__(self, initialise=False):
        self.reg = [""] * 32  # 32 registers

        self.reg[0] = format(0, '032b')  # $zero register
        self.reg[31] = format(0, '032b')  # $ra = 0 (default = exit main())
        self.reg[29] = format(4 * 1023, '032b')  # $sp = 4092 (default pointing to top address in the memory)
        self.reg[30] = format(4 * 1023, '032b')  # $fp = 4092 (default pointing to top address in the memory)

        # Initialize registers if specified
        if initialise:
            for i in range(1, 29):
                self.reg[i] = format(0, '032b')  # Initialize s0-s7 and temporaries with 0's
            self.reg[8] = format(5, '032b')  # $t0 = 5
            self.reg[9] = format(10, '032b')  # $t1 = 10
            self.reg[10] = format(1, '032b')  # $t2 = 1
            self.reg[12] = format(20, '032b')  # $t4 = 20

    def write(self, number, binStr32):
        if number==0: # skip writing to $0
            return
        self.reg[number] = binStr32  # Store value as binary string

    def read(self, number):
        return signedVal(self.reg[number])  # Convert binary string to integer

    def reset(self, initialise=False):
        """Reset all registers to their initial state."""
        self.reg = [""] * 32  # Clear all registers
        self.reg[0] = format(0, '032b')  # Ensure $zero register remains 0

        if initialise:
            for i in range(8, 26):
                self.reg[i] = format(0, '032b')  # Initialize s0-s7 and temporaries with 0's
            self.reg[16] = format(5, '032b')  # $s0 = 5
            self.reg[17] = format(10, '032b')  # $s1 = 10
            self.reg[18] = format(1, '032b')  # $s2 = 1

    def get_registers(self):
        return self.reg

    def __getitem__(self, key):
        return self.reg[key]

    def __setitem__(self, key, value):
        self.reg[key] = value


# Testing commands for the Registers class
if __name__ == "__main__":
    # Initialize registers with default values
    registers = Registers(initialise=True)

    # Test reading the $zero register
    assert registers.read(0) == format(0, '032b'), "Error: $zero register should be 0"
    print("Test 1 Passed: $zero register is correctly initialized to 0.")

    # Test reading other registers after initialization
    assert registers.read(16) == format(5, '032b'), "Error: $s0 register should be 5"
    assert registers.read(17) == format(10, '032b'), "Error: $s1 register should be 10"
    assert registers.read(18) == format(1, '032b'), "Error: $s2 register should be 1"
    print("Test 2 Passed: $s0, $s1, and $s2 registers are correctly initialized.")

    # Test reading uninitialized registers
    for i in range(8, 32):
        if i not in [16, 17, 18, 29, 30, 31]:  # Skip the initialized registers
            assert registers.read(i) == format(0, '032b'), f"Error: Register ${i} should be 0"
    print("Test 3 Passed: Uninitialized registers are correctly set to 0.")

    # Test writing to registers
    registers.write(1, format(15, '032b'))  # Writing value 15 to $at register
    assert registers.read(1) == format(15, '032b'), "Error: $at register should be 15 after writing"
    print("Test 4 Passed: Successfully wrote and read value in $at register.")

    # Test attempt to write to $zero register
    registers.write(0, format(100, '032b'))  # Attempting to write 100 to $zero
    assert registers.read(0) == format(0, '032b'), "Error: $zero register should remain 0 after attempted write"
    print("Test 5 Passed: $zero register cannot be modified.")

    # Test reset function
    registers.reset()
    assert registers.read(0) == format(0, '032b'), "Error: $zero register should be 0 after reset"
    for i in range(1, 32):
        assert registers.read(i) == "", f"Error: Register ${i} should be uninitialized after reset"
    print("Test 6 Passed: All registers reset correctly.")
