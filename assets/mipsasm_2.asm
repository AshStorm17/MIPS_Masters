add $t0, $t1, $t2       # $t0 = $t1 + $t2
sub $t3, $t4, $t5       # $t3 = $t4 - $t5
sw $t0, 0($sp)
lw $t5, 0($sp)
addi $t6, $t5, 7
jr $ra