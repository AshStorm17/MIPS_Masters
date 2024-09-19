main:
li $t0, 30


li $t1, 20
add $a0, $t0, $t1

li $v0, 1

syscall


la $a0, str


li $v0, 4

syscall


li $v0, 0
jr $ra
  