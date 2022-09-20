org=0
.section .text
.globl _start
_start:
    li t1, 42
    li t2, 48
    add t3, t1, t2
    li sp,0x800
    j main
    slt x0,x0,x0

.section .bss.stack
.global boot_stack
boot_stack:
.space 2048*4
.global boot_stack_top
boot_stack_top:





