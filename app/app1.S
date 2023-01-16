	.file	"app1.c"
	.option nopic
	.text
	.globl	i
	.section	.sdata,"aw"
	.align	2
	.type	i, @object
	.size	i, 4
i:
	.word	-559038737
	.globl	row
	.align	2
	.type	row, @object
	.size	row, 4
row:
	.word	1515870810
	.globl	j
	.align	2
	.type	j, @object
	.size	j, 4
j:
	.word	305419896
	.globl	charcol
	.align	2
	.type	charcol, @object
	.size	charcol, 4
charcol:
	.word	-1515870811
	.globl	fontp
	.align	2
	.type	fontp, @object
	.size	fontp, 4
fontp:
	.word	286331153
	.globl	fontp2
	.align	2
	.type	fontp2, @object
	.size	fontp2, 4
fontp2:
	.word	572662306
	.globl	r
	.align	2
	.type	r, @object
	.size	r, 4
r:
	.word	858993459
	.globl	pointer
	.section	.sbss,"aw",@nobits
	.align	2
	.type	pointer, @object
	.size	pointer, 4
pointer:
	.zero	4
	.globl	screen
	.data
	.align	2
	.type	screen, @object
	.size	screen, 512
screen:
	.string	"scrt\001\002\003\004\001\002\003\004U\252U\252"
	.zero	495
	.globl	font
	.align	2
	.type	font, @object
	.size	font, 208
font:
	.string	"0x\314\314\374\314\314"
	.string	"\374ff|ff\374"
	.string	"<f\300\300\300f<"
	.string	"\370lfffl\370"
	.string	"\376bhxhb\376"
	.string	"\376bhxh`\360"
	.string	"<f\300\300\316f>"
	.string	"\314\314\314\374\314\314\314"
	.string	"x00000x"
	.string	"\036\f\f\f\314\314x"
	.string	"\346flxlf\346"
	.string	"\360```bf\376"
	.string	"\306\356\376\376\326\306\306"
	.string	"\306\346\366\336\316\306\306"
	.string	"8l\306\306\306l8"
	.string	"\374ff|``\360"
	.string	"x\314\314\314\334x\034"
	.string	"\374ff|lf\346"
	.string	"x\314\340p\034\314x"
	.string	"\374\2640000x"
	.string	"\314\314\314\314\314\314\374"
	.string	"\314\314\314\314\314x0"
	.string	"\306\306\306\326\376\356\306"
	.string	"\306\306l88l\306"
	.string	"\314\314\314x00x"
	.string	"\376\306\214\0302f\376"
	.globl	hello
	.align	2
	.type	hello, @object
	.size	hello, 24
hello:
	.string	"HELLO WORLD HELLO WORLD"
	.text
	.align	2
	.globl	printchar
	.type	printchar, @function
printchar:
	addi	sp,sp,-48
	sw	s0,44(sp)
	addi	s0,sp,48
	mv	a5,a0
	sw	a1,-40(s0)
	sw	a2,-44(s0)
	sb	a5,-33(s0)
	lbu	a5,-33(s0)
	addi	a4,a5,-65
	lui	a5,%hi(fontp)
	sw	a4,%lo(fontp)(a5)
	lui	a5,%hi(fontp)
	lw	a5,%lo(fontp)(a5)
	slli	a4,a5,3
	lui	a5,%hi(fontp)
	sw	a4,%lo(fontp)(a5)
	lw	a5,-40(s0)
	slli	a4,a5,7
	lw	a5,-44(s0)
	add	a4,a4,a5
	lui	a5,%hi(r)
	sw	a4,%lo(r)(a5)
	lui	a5,%hi(fontp)
	lw	a5,%lo(fontp)(a5)
	addi	a4,a5,8
	lui	a5,%hi(fontp2)
	sw	a4,%lo(fontp2)(a5)
	lui	a5,%hi(fontp)
	lw	a5,%lo(fontp)(a5)
	sw	a5,-20(s0)
	j	.L2
.L3:
	lui	a5,%hi(r)
	lw	a5,%lo(r)(a5)
	addi	a4,a5,16
	lui	a5,%hi(r)
	sw	a4,%lo(r)(a5)
	lui	a5,%hi(r)
	lw	a5,%lo(r)(a5)
	lui	a4,%hi(font)
	addi	a3,a4,%lo(font)
	lw	a4,-20(s0)
	add	a4,a3,a4
	lbu	a4,0(a4)
	lui	a3,%hi(screen)
	addi	a3,a3,%lo(screen)
	add	a5,a3,a5
	sb	a4,0(a5)
	lw	a5,-20(s0)
	addi	a5,a5,1
	sw	a5,-20(s0)
.L2:
	lui	a5,%hi(fontp2)
	lw	a5,%lo(fontp2)(a5)
	lw	a4,-20(s0)
	blt	a4,a5,.L3
	nop
	nop
	lw	s0,44(sp)
	addi	sp,sp,48
	jr	ra
	.size	printchar, .-printchar
	.align	2
	.globl	putchar
	.type	putchar, @function
putchar:
	addi	sp,sp,-64
	sw	ra,60(sp)
	sw	s0,56(sp)
	addi	s0,sp,64
	sw	a0,-52(s0)
	lw	a4,-52(s0)
	li	a5,10
	bne	a4,a5,.L5
	sw	zero,-20(s0)
	sw	zero,-24(s0)
	lui	a5,%hi(pointer)
	lw	a5,%lo(pointer)(a5)
	sw	a5,-20(s0)
	j	.L6
.L7:
	lw	a5,-20(s0)
	addi	a5,a5,-16
	sw	a5,-20(s0)
	lw	a5,-24(s0)
	addi	a5,a5,1
	sw	a5,-24(s0)
.L6:
	lw	a4,-20(s0)
	li	a5,15
	bgt	a4,a5,.L7
	lw	a5,-24(s0)
	addi	a5,a5,1
	sw	a5,-24(s0)
	lw	a5,-24(s0)
	slli	a4,a5,4
	lui	a5,%hi(pointer)
	sw	a4,%lo(pointer)(a5)
	j	.L4
.L5:
	lw	a4,-52(s0)
	li	a5,13
	bne	a4,a5,.L9
	lui	a5,%hi(pointer)
	lw	a5,%lo(pointer)(a5)
	addi	a4,a5,16
	lui	a5,%hi(pointer)
	sw	a4,%lo(pointer)(a5)
	j	.L4
.L9:
	lw	a4,-52(s0)
	li	a5,9
	bne	a4,a5,.L10
	sw	zero,-28(s0)
	sw	zero,-32(s0)
	lui	a5,%hi(pointer)
	lw	a5,%lo(pointer)(a5)
	sw	a5,-28(s0)
	j	.L11
.L12:
	lw	a5,-28(s0)
	addi	a5,a5,-4
	sw	a5,-28(s0)
	lw	a5,-32(s0)
	addi	a5,a5,1
	sw	a5,-32(s0)
.L11:
	lw	a4,-28(s0)
	li	a5,3
	bgt	a4,a5,.L12
	lw	a5,-32(s0)
	addi	a5,a5,1
	sw	a5,-32(s0)
	lw	a5,-32(s0)
	slli	a4,a5,2
	lui	a5,%hi(pointer)
	sw	a4,%lo(pointer)(a5)
	j	.L4
.L10:
	lw	a4,-52(s0)
	li	a5,32
	bne	a4,a5,.L13
	lui	a5,%hi(pointer)
	lw	a5,%lo(pointer)(a5)
	addi	a4,a5,1
	lui	a5,%hi(pointer)
	sw	a4,%lo(pointer)(a5)
	j	.L4
.L13:
	sw	zero,-36(s0)
	sw	zero,-40(s0)
	sw	zero,-44(s0)
	lui	a5,%hi(pointer)
	lw	a5,%lo(pointer)(a5)
	sw	a5,-36(s0)
	j	.L14
.L15:
	lw	a5,-36(s0)
	addi	a5,a5,-16
	sw	a5,-36(s0)
	lw	a5,-40(s0)
	addi	a5,a5,1
	sw	a5,-40(s0)
.L14:
	lw	a4,-36(s0)
	li	a5,15
	bgt	a4,a5,.L15
	lw	a5,-36(s0)
	addi	a5,a5,-16
	sw	a5,-44(s0)
	lw	a5,-52(s0)
	andi	a5,a5,0xff
	lw	a2,-44(s0)
	lw	a1,-40(s0)
	mv	a0,a5
	call	printchar
	lui	a5,%hi(pointer)
	lw	a5,%lo(pointer)(a5)
	addi	a4,a5,1
	lui	a5,%hi(pointer)
	sw	a4,%lo(pointer)(a5)
.L4:
	lw	ra,60(sp)
	lw	s0,56(sp)
	addi	sp,sp,64
	jr	ra
	.size	putchar, .-putchar
	.align	2
	.globl	putstr
	.type	putstr, @function
putstr:
	addi	sp,sp,-48
	sw	ra,44(sp)
	sw	s0,40(sp)
	addi	s0,sp,48
	sw	a0,-36(s0)
	sw	zero,-20(s0)
	j	.L17
.L18:
	lw	a5,-20(s0)
	lw	a4,-36(s0)
	add	a5,a4,a5
	lbu	a5,0(a5)
	sb	a5,-21(s0)
	lw	a5,-20(s0)
	addi	a5,a5,1
	sw	a5,-20(s0)
	lbu	a5,-21(s0)
	mv	a0,a5
	call	putchar
.L17:
	lw	a5,-20(s0)
	lw	a4,-36(s0)
	add	a5,a4,a5
	lbu	a5,0(a5)
	bne	a5,zero,.L18
	nop
	nop
	lw	ra,44(sp)
	lw	s0,40(sp)
	addi	sp,sp,48
	jr	ra
	.size	putstr, .-putstr
	.align	2
	.globl	uart
	.type	uart, @function
uart:
	addi	sp,sp,-48
	sw	s0,44(sp)
	addi	s0,sp,48
	sw	a0,-36(s0)
	sw	zero,-20(s0)
	j	.L20
.L21:
	lw	a5,-20(s0)
	lw	a4,-36(s0)
	add	a5,a4,a5
	lbu	a4,0(a5)
	lui	a5,%hi(screen)
	addi	a5,a5,%lo(screen)
	sb	a4,0(a5)
	lw	a5,-20(s0)
	addi	a5,a5,1
	sw	a5,-20(s0)
.L20:
	lw	a5,-20(s0)
	lw	a4,-36(s0)
	add	a5,a4,a5
	lbu	a5,0(a5)
	bne	a5,zero,.L21
	nop
	nop
	lw	s0,44(sp)
	addi	sp,sp,48
	jr	ra
	.size	uart, .-uart
	.align	2
	.globl	main
	.type	main, @function
main:
	addi	sp,sp,-16
	sw	ra,12(sp)
	sw	s0,8(sp)
	addi	s0,sp,16
	lui	a5,%hi(pointer)
	sw	zero,%lo(pointer)(a5)
	lui	a5,%hi(hello)
	addi	a0,a5,%lo(hello)
	call	putstr
	nop
	lw	ra,12(sp)
	lw	s0,8(sp)
	addi	sp,sp,16
	jr	ra
	.size	main, .-main
	.ident	"GCC: (xPack GNU RISC-V Embedded GCC, 64-bit) 10.1.0"
