from pymem import PyMEM
from pyriscv_regs import PyRiscvRegs
from pyriscv_types import *    
from pyriscv_riscv_def import *    
from pyriscv_operator import *   

    
class PyRiscv:
    def __init__(self,imem,reset_vec=0,bw=32):
        self._imem = imem
        self._pc   = reset_vec
        self._regs = PyRiscvRegs(32,bw)
        self._operator = PyRiscvOperator(bw)
        self.__control()
        
    def __control(self):
        self._exit = False
        while not self._exit:
            inst = self.__stage_if(self._pc)
            decode_map = self.__stage_decode(inst)
            self.__stage_exec(decode_map)
        
        
    def __stage_if(self,pc):
        return PyRiscvLogic(
            self._imem[pc] + 
            (self._imem[pc+1] << 8) + 
            (self._imem[pc+2] << 16) + 
            (self._imem[pc+3] << 24))
    
    def __stage_decode(self,w):
        decode_map = PyRiscvStruct()
        decode_map.CODECLASS           = PYRSISCV_CODECLASS.FV(w[1:0])
        decode_map.OPCODE              = PYRSISCV_OPCODE.FV(w[6:2])
        decode_map.FUNCT3_OP_IMM_OP    = PYRSISCV_FUNCT3_OP_IMM_OP.FV(w[14:12])
        decode_map.FUNCT3_BRANCH       = PYRSISCV_FUNCT3_BRANCH.FV(w[14:12])
        decode_map.FUNCT7              = w[31:25]
        decode_map.RD                  = w[11:7]
        decode_map.RS1                 = w[19:15]
        decode_map.RS2                 = w[24:20]
        decode_map.IMMJ                = PyRiscvOperator(21).signed((w[30:21]<<1) | (w[20] << 11)   | (w[19:12] << 12) | (w[31] << 20))
        decode_map.IMMB                = PyRiscvOperator(13).signed((w[11:8]<<1)  | (w[30:25] << 5) | (w[7] << 11)     | (w[31] << 12))
        decode_map.IMMI                = PyRiscvOperator(12).signed(w[31:20])
        decode_map.IMMU                = w[31:12] << 12
        decode_map.EXIT                = (int(w) == 0x00002033)
        
        #FUNCT7
        if decode_map.FUNCT7 == 0x20:
            if decode_map.FUNCT3_OP_IMM_OP == PYRSISCV_FUNCT3_OP_IMM_OP.ADD:
                decode_map.FUNCT3_OP_IMM_OP = PYRSISCV_FUNCT3_OP_IMM_OP.SUB
            elif decode_map.FUNCT3_OP_IMM_OP == PYRSISCV_FUNCT3_OP_IMM_OP.SRL:
                decode_map.FUNCT3_OP_IMM_OP = PYRSISCV_FUNCT3_OP_IMM_OP.SRA
        return decode_map
    
    def __stage_exec(self,decode_map):
        
        if decode_map.OPCODE == PYRSISCV_OPCODE.JAL:
            self._regs[decode_map.RD] = self._pc + 4
            self._pc = decode_map.IMMJ
        elif decode_map.OPCODE == PYRSISCV_OPCODE.JALR:
            self._regs[decode_map.RD] = self._pc + 4
            self._pc = ((decode_map.IMM + self._regs[decode_map.RS1]) | 0x1) - 1 + self._pc
        elif decode_map.OPCODE == PYRSISCV_OPCODE.BRANCH:
            if self._operator(decode_map.FUNCT3_BRANCH,self._regs[decode_map.RS1],self._regs[decode_map.RS2]):
                self._pc += decode_map.IMMB
            else:
                self._pc += 4
        elif decode_map.OPCODE == PYRSISCV_OPCODE.OP_IMM:
            self._regs[decode_map.RD] = self._operator(decode_map.FUNCT3_OP_IMM_OP,self._regs[decode_map.RS1],decode_map.IMMI)
            self._pc += 4
        elif decode_map.OPCODE == PYRSISCV_OPCODE.OP:
            self._regs[decode_map.RD] = self._operator(decode_map.FUNCT3_OP_IMM_OP,self._regs[decode_map.RS1],self._regs[decode_map.RS2]) 
            self._pc += 4
        elif decode_map.OPCODE == PYRSISCV_OPCODE.LUI:
            self._regs[decode_map.RD] = decode_map.IMMU
            self._pc += 4
        elif decode_map.OPCODE == PYRSISCV_OPCODE.AUIPC:
            self._pc += decode_map.IMMU
            self._regs[decode_map.RD] = self._pc           
        if decode_map.EXIT:
            self._exit = True
    
if __name__ == '__main__':
    import sys
    imem = PyMEM(sys.argv[1])
    PyRiscv(imem)
