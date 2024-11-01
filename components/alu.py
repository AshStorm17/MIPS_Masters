# -------------------------------------------
# ALU class and operations
def signedVal(num):
    """Convert a signed integer to its value based on 2's complement representation."""
    return num - ((num >> 31) & 1) * (1 << 32)

def signedBin(num):
    """Return the 2's complement binary string of a given integer."""
    if num < 0:
        return bin(num % (1 << 32))[2:]
    return format(num & (1 << 32) - 1, '032b')  # Ensure it fits in 32 bits

# ---------------------------

class ALU:
    def __init__(self):
        pass

    def alu_shift(self, operation, opr1, shamt):
        """Perform shift operations."""
        match operation:
            case "000000":  # sll
                return opr1 << shamt  # Left shift
            case "000010":  # srl
                return opr1 >> shamt  # Logical right shift
            case "000011":  # sra
                return opr1 >> shamt  # Arithmetic right shift

    def alu_arith(self, operation, opr1, opr2):
        """Perform arithmetic operations."""
        match operation:
            case "100000":  # add
                return signedVal(opr1 + opr2)
            case "100010":  # sub
                return signedVal(opr1 - opr2)
            case "100100":  # and
                return opr1 & opr2
            case "100101":  # or
                return opr1 | opr2
            case "101010":  # slt
                return 1 if signedVal(opr1) < signedVal(opr2) else 0
            case "101011":  # sltu
                return 1 if (opr1 < opr2) else 0
            case "100111":  # nor
                return ~(opr1 | opr2) & 0xFFFFFFFF  # Mask to ensure it fits in 32 bits

    def alu_arith_i(self, operation, src, immediate):
        """Perform immediate arithmetic operations."""
        match operation:
            case "000":  # addi
                return signedVal(src + immediate)
            case "010":  # slti
                return 1 if src < immediate else 0
            case "011":  # sltiu
                return 1 if src < immediate else 0
            case "100":  # andi
                return src & immediate
            case "101":  # ori
                return src | immediate
            case "111":  # lui
                return immediate << 16

    def giveAddr(self, baseAddr, lower16bits):
        """
        Compute the memory address for load/store instructions 
        by adding the base address and the sign-extended lower 16 bits.
        """
        offset = signedVal(lower16bits)
        return baseAddr + offset  # Return the final computed address
    
    def isEqual(self, int1, int2):
        """
        Compare two integers for equality, used in branch instructions.
        """
        return int1 == int2  # Direct comparison of integers

# --------------------------------------------
