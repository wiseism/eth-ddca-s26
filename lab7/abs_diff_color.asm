# O32: a0=R1 a1=G1 a2=B1 a3=R2, G2 at incoming sp+16, B2 at sp+20.
# Link with abs_diff from lab7_sad.asm. All used s-registers are preserved.
.text
abs_diff_color:
    addi $sp, $sp, -48
    sw $s0, 16($sp)
    sw $s1, 20($sp)
    sw $s2, 24($sp)
    sw $s3, 28($sp)
    sw $s4, 32($sp)
    sw $s5, 36($sp)
    sw $s6, 40($sp)
    sw $ra, 44($sp)
    add $s0, $a0, $zero
    add $s1, $a1, $zero
    add $s2, $a2, $zero
    add $s3, $a3, $zero
    lw $s4, 64($sp)
    lw $s5, 68($sp)
    add $a0, $s0, $zero
    add $a1, $s3, $zero
    jal abs_diff
    sll $zero, $zero, 0
    add $s6, $v0, $zero
    add $a0, $s1, $zero
    add $a1, $s4, $zero
    jal abs_diff
    sll $zero, $zero, 0
    add $s6, $s6, $v0
    add $a0, $s2, $zero
    add $a1, $s5, $zero
    jal abs_diff
    sll $zero, $zero, 0
    add $v0, $s6, $v0
    lw $s0, 16($sp)
    lw $s1, 20($sp)
    lw $s2, 24($sp)
    lw $s3, 28($sp)
    lw $s4, 32($sp)
    lw $s5, 36($sp)
    lw $s6, 40($sp)
    lw $ra, 44($sp)
    addi $sp, $sp, 48
    jr $ra
    sll $zero, $zero, 0
