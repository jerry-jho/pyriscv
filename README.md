# pyriscv
A RISCV Emulator written in Python

Requires:
  python3.4+
  
No other libraries!!

# run

    cd app
    $riscv-gcc -g -march=rv32i -mabi=ilp32  app.S -nostdlib -Tlink.ld -o app.elf
    $riscv-objdump -S -d app.elf > app.lst
    $riscv-objcopy -F verilog app.elf app.mem
    python3 ../src/pyriscv.py app.mem

All data write to x0 will print to console
