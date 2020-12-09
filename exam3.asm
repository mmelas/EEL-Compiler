j Lmain
L0:
Lmain: 
add $sp,$sp,60
move $s0,$sp
L1: lw $t1,-12($s0)
lw $t2,-16($s0)
add $t1,$t1,$t2
sw $t1,-44($s0)
L2: lw $t1,-44($s0)
lw $t2,-20($s0)
bgt $t1,$t2,L4
L3: j L12
L4: lw $t1,-24($s0)
lw $t2,-28($s0)
ble $t1,$t2,L6
L5: j L11
L6: lw $t1,-32($s0)
lw $t2,-24($s0)
add $t1,$t1,$t2
sw $t1,-48($s0)
L7: lw $t1,-48($s0)
sw $t1,-32($s0)
L8: lw $t1,-24($s0)
li $t2,1
add $t1,$t1,$t2
sw $t1,-52($s0)
L9: lw $t1,-52($s0)
sw $t1,-24($s0)
L10: j L4
L11: j L20
L12: lw $t1,-16($s0)
lw $t2,-20($s0)
bgt $t1,$t2,L16
L13: j L14
L14: lw $t1,-16($s0)
lw $t2,-36($s0)
blt $t1,$t2,L16
L15: j L18
L16: li $t1,3
sw $t1,-36($s0)
L17: j L20
L18: lw $t1,-16($s0)
lw $t2,-20($s0)
add $t1,$t1,$t2
sw $t1,-56($s0)
L19: lw $t1,-56($s0)
sw $t1,-40($s0)
L20:
L21:
