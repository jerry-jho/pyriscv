..\..\..\riscvgcc\xpgcc\bin\riscv-none-embed-gcc.exe -g -march=rv32i -mabi=ilp32 app1.S -nostdlib -Tlink.ld -o app1.elf
..\..\..\riscvgcc\xpgcc\bin\riscv-none-embed-objdump -S -d app1.elf > app1.lst
..\..\..\riscvgcc\xpgcc\bin\riscv-none-embed-objcopy -F verilog app1.elf app1.mem
python ../src/pyriscv.py app1.mem
