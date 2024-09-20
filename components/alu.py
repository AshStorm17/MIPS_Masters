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
        # Note: return binary string as answer
        ans = ""
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
        return ans

    def alu_arith_i(self, operation, src, immediate):
        opr1 = signedVal(src)
        imm = signedVal(immediate)
        match operation:
            case "000":
                # addi
                ans = opr1 + imm
            case "010":
                # slti
                ans = 1 if opr1 < imm else 0
            case "011":
                # sltiu
                ans = 1 if int(src, 2) < int(immediate, 2) else 0
            case "100":
                # andi
                ans = opr1 & imm
            case "101":
                # ori
                ans = opr1 | imm
            case "111":
                # lui
                ans = imm << 16
        ans_str = format(ans, '032b')
        return ans_str

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
        return signedVal(bin1)-signedVal(bin2)==0 # directly compare the two 32-bit binary strings


# --------------------------------------------
