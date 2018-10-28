.section .vectors, "ax"
.org 0x0
    j _start

.section .text
.globl _start
_start:
    li t1, 42
    li t2, 48
    add t3, t1, t2
    mv x0 ,t3
    slt x0,x0,x0