# Test MIPS Assembly Code for Assembler

# Arithmetic operations
add $t0, $t1, $t2       # $t0 = $t1 + $t2
sub $t3, $t4, $t5       # $t3 = $t4 - $t5
and $t6, $t7, $t8       # $t6 = $t7 & $t8
or  $t9, $t0, $t3       # $t9 = $t0 | $t3
sll $a0, $a1, 4         # $a0 = $a1 << 4
srl $a2, $a3, 2         # $a2 = $a3 >> 2

# Immediate operations
addi $t0, $t1, 10       # $t0 = $t1 + 10
andi $t2, $t3, 0xFF     # $t2 = $t3 & 0xFF
ori  $t4, $t5, 0x0F     # $t4 = $t5 | 0x0F
xori $t6, $t7, 0xF0     # $t6 = $t7 ^ 0xF0

# Memory operations
lw   $t0, 0($sp)        # $t0 = Mem[$sp]
sw   $t1, 4($sp)        # Mem[$sp+4] = $t1
lh   $t2, 8($sp)        # $t2 = Mem[$sp+8] (half-word load)
lhu  $t3, 12($sp)       # $t3 = Mem[$sp+12] (half-word unsigned load)
lb   $t4, 16($sp)       # $t4 = Mem[$sp+16] (byte load)
lbu  $t5, 20($sp)       # $t5 = Mem[$sp+20] (byte unsigned load)
sh   $t6, 24($sp)       # Mem[$sp+24] = $t6 (store half-word)
sb   $t7, 28($sp)       # Mem[$sp+28] = $t7 (store byte)

# Branching and jumps
beq  $t0, $t1, subroutine   # If $t0 == $t1, jump to label1
bne  $t2, $t3, subroutine   # If $t2 != $t3, jump to label2

# Conditional branch (using slti, sltiu)
slti $t4, $t5, 100      # If $t5 < 100, $t4 = 1 else $t4 = 0
sltiu $t6, $t7, 1000    # If unsigned $t7 < 1000, $t6 = 1 else $t6 = 0

# Jump operations
j main                  # Jump to main
jal subroutine          # Jump to subroutine and link

subroutine:
  # Subroutine code
  jr $ra                 # Return from subroutine

main:
    syscall