#
# Calculate sum from A to B.
#
# Authors: 
#	X Y, Z Q 
#
# Group: ...
#

.text
main:
	addi $t0, $zero, 5       # A, positive signed 16-bit input
	addi $t1, $zero, 10      # B >= A
	add  $t2, $zero, $zero
range_loop:
	add  $t2, $t2, $t0
	beq  $t0, $t1, end
	add  $zero, $zero, $zero # harmless with or without branch delay slots
	addi $t0, $t0, 1
	j    range_loop
	add  $zero, $zero, $zero
end:	
	j	end	# Infinite loop at the end of the program. 
	add $zero, $zero, $zero
