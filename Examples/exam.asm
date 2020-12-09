j Lmain
L0:
sw $ra,($sp)
L1: lw $t0,-4($sp)
add $t0,$t0,-12
lw $t1,($t0)
sw $t1,-12($sp)
L2: lw $t0,-4($sp)
add $t0,$t0,-16
lw $t0,($t0)
lw $t1,($t0)
lw $t0,-16($sp)
sw $t1,($t0)
L3:
lw $ra,($sp)
jr $ra
L4:
sw $ra,($sp)
L5: lw $t1,-12($sp)
lw $t0,-16($sp)
sw $t1,($t0)
L6: add $fp,$sp,20
lw $t0,-12($s0)
sw $t0,-12($fp)
L7: lw $t0,-4($sp)
add $t0,$t0,-16
sw $t0,-16($fp)
L8: lw $t0,-4($sp)
sw $t0,-4($fp)
add $sp,$sp,20
jal L0
add $sp,$sp,-20
L9:
lw $ra,($sp)
jr $ra
L10:
Lmain: 
add $sp,$sp,20
move $s0,$sp
L11: add $fp,$sp,20
lw $t0,-12($s0)
sw $t0,-12($fp)
L12: add $t0,$sp,-16
sw $t0,-16($fp)
L13: lw $t0,-4($sp)
sw $t0,-4($fp)
add $sp,$sp,20
jal L4
add $sp,$sp,-20
L14:
L15:
