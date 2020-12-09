j Lmain
L0:
sw $ra,($sp)
L1: lw $t1,-12($s0)
lw $t0,-4($sp)
add $t0,$t0,-12
lw $t2,($t0)
add $t1,$t1,$t2
sw $t1,-20($sp)
L2: lw $t1,-20($sp)
lw $t0,-4($sp)
add $t0,$t0,-24
lw $t2,($t0)
bgt $t1,$t2,L4
L3: j L11
L4: lw $t0,-12($sp)
lw $t1,($t0)
lw $t0,-4($sp)
add $t0,$t0,-24
lw $t2,($t0)
blt $t1,$t2,L6
L5: j L10
L6: lw $t0,-12($sp)
lw $t1,($t0)
li $t2,1
add $t1,$t1,$t2
sw $t1,-24($sp)
L7: lw $t1,-24($sp)
sw $t1,-16($sp)
L8: lw $t1,-16($sp)
lw $t0,-4($sp)
add $t0,$t0,-12
sw $t1,($t0)
L9: j L4
L10: j L15
L11: add $fp,$sp,32
lw $t0,-4($sp)
lw $t0,-4($t0)
add $t0,$t0,-12
sw $t0,-12($fp)
L12: add $t0,$sp,-28
sw $t0,-8($fp)
L13: sw $sp,-4($fp)
add $sp,$sp,32
jal L0
add $sp,$sp,-32
L14: lw $t1,-28($sp)
lw $t0,-4($sp)
add $t0,$t0,-12
sw $t1,($t0)
L15: lw $t1,-16($sp)
lw $t0,-8($sp)
sw $t1,($t0)
L16:
lw $ra,($sp)
jr $ra
L17:
sw $ra,($sp)
L18: lw $t1,-12($sp)
lw $t0,-8($sp)
sw $t1,($t0)
L19:
lw $ra,($sp)
jr $ra
L20:
Lmain: 
add $sp,$sp,28
move $s0,$sp
L21: add $fp,$sp,28
lw $t0,-12($s0)
sw $t0,-12($fp)
L22: add $t0,$sp,-24
sw $t0,-8($fp)
L23: lw $t0,-4($sp)
sw $t0,-4($fp)
add $sp,$sp,28
jal L17
add $sp,$sp,-28
L24: lw $t1,-24($s0)
sw $t1,-12($s0)
L25:
L26:
