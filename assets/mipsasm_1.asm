add $t0, $t1, $t2       # $t0 = $t1 + $t2
sub $t3, $t4, $t5       # $t3 = $t4 - $t5
beq $t3, $t4, done
addi $t7, $t0, 10 
done: 
add $t0, $t3, $t4
jr $ra
syscall