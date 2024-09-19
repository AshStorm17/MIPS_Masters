# -------------------------------------------
# ALU class and operations
def signedVal(binStr):
    isSigned = int(binStr[0]=="1")
    return int(binStr, 2) - isSigned*(2**len(binStr))

def signedBin(num):
    # return 2's complement binary string of length len
    ans=""
    if(num<0):
        ans = bin(num % (1<<32))[2:]
    else:
        ans = format(num, '032b')
    return ans
# ---------------------------

# ---------------------------
class ALU:
    def __init__(self):
        pass

    def alu_shift(self, operation, opr1, shamt):
        match operation:
            case "000000":
                return format(int(opr1, 2) << shamt, '032b')
            case "000010":
                if opr1 < 0:
                    opr1 = opr1 + (1 << 32)
                return format(int(opr1, 2) >> shamt, '032b')
            case "000011":
                return format(int(opr1, 2) >> shamt, '032b')
    
    def alu_arith(self, operation, opr1, opr2):
        """
        COAHP: For the R-type instructions, the ALU needs to perform one of the five actions (AND, OR, subtract, add, or set on less than
        """
        # Note: return binary string as answer
        ans = ""
        match operation:
            case "100000": # add
                ans = signedBin(signedVal(opr1) + signedVal(opr2))
                pass
            case "100010": # sub
                ans = signedBin(signedVal(opr1) - signedVal(opr2))
            case "100100": # and
                ans = signedVal(opr1) & signedVal(opr2)
            case "100101": # or
                ans = signedVal(opr1) | signedVal(opr2)
            case "101010": #slt 
                # compare and return 1 or 0
                return int(signedVal(opr1) < signedVal(opr2))
        
        return ans

    def giveAddr(self, baseAddr, lower16bits):
        """
        COAHP: For load word and store word instructions, 
        we use the ALU to compute the memory address by addition.
        The ALU computes the sum of the value read from the register file and the
        sign-extended, lower 16 bits of the instruction (offset).
        """
        offset = signedVal(lower16bits)
        baseAddrVal = int(baseAddr, 2)
        return format(baseAddrVal+offset, '032b') # assumed final address not -ve
    
    def isEqual(self, bin1, bin2): # comparison for bne, beq
        """
        COAHP: For branch equal, the ALU must perform a subtraction.
        """
        return bin1==bin2 # directly compare the two 32-bit binary strings


# --------------------------------------------