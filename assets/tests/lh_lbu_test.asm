addi $t9, $t9, 1000 
lh $t7, 0($t9)          # check $t7 = -1265
lbu $t8, 0($t9)         # check $t8 = 251
jr $ra