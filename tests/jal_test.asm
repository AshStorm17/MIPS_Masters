addi $t2, $0, 5
addi $sp, $sp, -4
sw $ra, 0($sp)
jal Next

lw $ra, 0($sp)
addi $sp, $sp, 4
addi $t4, $0, 10
syscall

Next:
addi $t3, $0, 20
addi $sp, $sp, -4
sw $ra, 0($sp)
jal Nextto
lw $ra, 0($sp)
addi $sp, $sp, 4
jr $ra

Nextto:
addi $t5, $0, 30
jr $ra