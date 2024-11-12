addi $t0, $0, 202   # $t0 = 0b11001010 (202 in decimal)
addi $t1, $0, 175   # $t1 = 0b10101111 (175 in decimal)
andi $t2, $t0, 240     # $t2 = $t0 & 0b11110000 -> 0b11000000 (192 in decimal)

# Test case 2: ori (bitwise OR with immediate)
ori $t3, $t1, 64      # $t3 = $t1 | 0b01000000 -> 0b11101111 (239 in decimal)

# Test case 3: and (bitwise AND)
and $t4, $t0, $t1             # $t4 = $t0 & $t1 -> 0b10001010 (138 in decimal)

# Test case 4: or (bitwise OR)
or $t5, $t0, $t1              # $t5 = $t0 | $t1 -> 0b11101111 (239 in decimal)

# Test case 5: nor (bitwise NOR)
nor $t6, $t0, $t1             # $t6 = ~( $t0 | $t1 ) -> 0b00000000 (0 in decimal)
jr $ra