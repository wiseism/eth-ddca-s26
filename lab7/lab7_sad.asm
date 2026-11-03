# ETH DDCA Lab7: 3x3 grayscale SAD, CompactDataAtZero.
# left: 0..32, right: 36..68, absolute differences: 72..104.
.text
.globl main
main:
    addi $sp, $zero, 12280  # 0x2ff8, eight-byte aligned
    add $s0, $zero, $zero
# INPUTS_BEGIN
    addi $t0, $zero, 5
    sw $t0, 0($s0)
    addi $t0, $zero, 16
    sw $t0, 4($s0)
    addi $t0, $zero, 7
    sw $t0, 8($s0)
    addi $t0, $zero, 1
    sw $t0, 12($s0)
    addi $t0, $zero, 1
    sw $t0, 16($s0)
    addi $t0, $zero, 13
    sw $t0, 20($s0)
    addi $t0, $zero, 2
    sw $t0, 24($s0)
    addi $t0, $zero, 8
    sw $t0, 28($s0)
    addi $t0, $zero, 10
    sw $t0, 32($s0)
    addi $t0, $zero, 4
    sw $t0, 36($s0)
    addi $t0, $zero, 15
    sw $t0, 40($s0)
    addi $t0, $zero, 8
    sw $t0, 44($s0)
    addi $t0, $zero, 0
    sw $t0, 48($s0)
    addi $t0, $zero, 2
    sw $t0, 52($s0)
    addi $t0, $zero, 12
    sw $t0, 56($s0)
    addi $t0, $zero, 3
    sw $t0, 60($s0)
    addi $t0, $zero, 7
    sw $t0, 64($s0)
    addi $t0, $zero, 11
    sw $t0, 68($s0)
# INPUTS_END
    addi $s1, $zero, 0
    addi $s2, $zero, 9
    addi $s3, $zero, 72
    addi $sp, $sp, -16     # outgoing argument home area
loop:
    beq $s1, $s2, end_loop
    sll $zero, $zero, 0
    sll $t0, $s1, 2
    add $t1, $s0, $t0
    lw $a0, 0($t1)
    lw $a1, 36($t1)
    jal abs_diff
    sll $zero, $zero, 0
    sll $t0, $s1, 2
    add $t1, $s3, $t0
    sw $v0, 0($t1)
    addi $s1, $s1, 1
    j loop
    sll $zero, $zero, 0
end_loop:
    add $a0, $s3, $zero
    add $a1, $s2, $zero
    jal recursive_sum
    sll $zero, $zero, 0
    add $t2, $v0, $zero
    addi $sp, $sp, 16
end:
    j end
    sll $zero, $zero, 0

abs_diff:
    sub $t0, $a0, $a1
    sra $t1, $t0, 31
    xor $t0, $t0, $t1
    sub $v0, $t0, $t1
    jr $ra
    sll $zero, $zero, 0

recursive_sum:
    beq $a1, $zero, sum_zero
    sll $zero, $zero, 0
    addi $sp, $sp, -32
    sw $a1, 20($sp)
    sw $a0, 24($sp)
    sw $ra, 28($sp)
    addi $a1, $a1, -1
    jal recursive_sum
    sll $zero, $zero, 0
    lw $t0, 20($sp)
    addi $t0, $t0, -1
    sll $t0, $t0, 2
    lw $t1, 24($sp)
    add $t0, $t1, $t0
    lw $t0, 0($t0)
    add $v0, $v0, $t0
    lw $ra, 28($sp)
    addi $sp, $sp, 32
    jr $ra
    sll $zero, $zero, 0
sum_zero:
    add $v0, $zero, $zero
    jr $ra
    sll $zero, $zero, 0
