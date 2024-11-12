addi $t2, $0, 5  #PC =0
addi $t3, $0, 5  #PC=4
beq $t2, $t3, 2   #PC=8  -> PC=8+4+2*4
addi $t2, $0, 10  #PC=16
addi $t2, $0, 20  #PC=20
addi $t2, $0, 35  #PC=24
syscall