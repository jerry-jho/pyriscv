del app1.mem
del app1.S
del app1.i
del app1.elf
del app1.1st


..\..\..\riscvgcc\xpgcc\bin\riscv-none-embed-gcc.exe -march=rv32i -mabi=ilp32 -E app1.c -nostdlib -o app1.i
..\..\..\riscvgcc\xpgcc\bin\riscv-none-embed-gcc.exe -march=rv32i -mabi=ilp32 -S app1.i -nostdlib -o app1.S
..\..\..\riscvgcc\xpgcc\bin\riscv-none-embed-gcc.exe -march=rv32i -mabi=ilp32 app.S app1.S -nostdlib -Tlink.ld -o app1.elf
..\..\..\riscvgcc\xpgcc\bin\riscv-none-embed-objdump -S -d app1.elf > app1.lst
..\..\..\riscvgcc\xpgcc\bin\riscv-none-embed-objcopy -F verilog app1.elf app1.mem
python ../src/pyriscv.py app1.mem



