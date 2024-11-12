addi $t0, $t0, 10    # $t0 = 10
addi $t1, $t1, 20    # $t1 = 20
sltiu $t2, $t0, 15   # $t2 = ($t0 < 15) ? (should be 1 since 10 < 15)

# Test case 2: Test sltiu where $t0 is equal to the immediate value
sltiu $t3, $t1, 20   # $t3 = ($t1 < 20) (should be 0 since 20 is not less than 20)

# Test case 3: Test sltiu where $t0 is greater than the immediate value
addi $t0, $t0, 20    # $t0 = 30 (previous value of $t0 was 10)
sltiu $t4, $t0, 20   # $t4 = ($t0 < 20) (should be 0 since 30 > 20)

syscall