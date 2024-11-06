# -------------------------------------------
# ALU class and operations
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
        opr1 = signedBin(opr1)
        opr2 = signedBin(opr2)
        match operation:
            case "100000": # add
                ans = signedBin(signedVal(opr1) + signedVal(opr2))
            case "100010": # sub
                ans = signedBin(signedVal(opr1) - signedVal(opr2))
            case "100100": # and
                ans = signedVal(opr1) & signedVal(opr2)
            case "100101": # or
                ans = signedVal(opr1) | signedVal(opr2)
            case "101010": #slt 
                ans = format(int(signedVal(opr1) < signedVal(opr2)), "032b")
            case "101011": # sltu
                ans = format(int(int(opr1,2) < int(opr2,2)), "032b")
            case "100111": # nor
                ans = format(~(signedVal(opr1) | signedVal(opr2)), "032b")
        return signedVal(ans)

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
