from pyriscv_types import *


class PYRSISCV_CODECLASS(PyRiscvEnum):
    BASE = 0b11

class PYRSISCV_OPCODE(PyRiscvEnum):
    LUI       = 0b01101
    AUIPC     = 0b00101
    JAL       = 0b11011
    JALR      = 0b11001
    BRANCH    = 0b11000
    OP_IMM    = 0b00100
    OP        = 0b01100
    LOAD      = 0b00000
    STORE     = 0b01000
    
class PYRSISCV_FUNCT3_OP_IMM_OP(PyRiscvEnum):
    ADD  = 0b000
    SUB  = 0b1000
    SLL  = 0b001
    SRL  = 0b101
    SRA  = 0b1101
    SLT  = 0b010
    SLTU = 0b011
    XOR  = 0b100
    OR   = 0b110
    AND  = 0b111
    
class PYRSISCV_FUNCT3_BRANCH(PyRiscvEnum):
    BEQ  = 0b000
    BNE  = 0b001
    BLT  = 0b100
    BGE  = 0b101
    BLTU = 0b110
    BGEU = 0b111
    
class PYRSISCV_FUNCT3_LOAD_STORE(PyRiscvEnum):
    B  = 0b000
    H  = 0b001
    W  = 0b010
    BU = 0b100
    HU = 0b101
