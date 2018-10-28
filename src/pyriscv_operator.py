
from pyriscv_riscv_def import *
import operator

class PyRiscvOperator:
    
    def __init__(self,bw):
        self._bw = bw
        self._exec_map = {
            PYRSISCV_FUNCT3_OP_IMM_OP.ADD  : self.add,
            PYRSISCV_FUNCT3_OP_IMM_OP.SUB  : self.sub,
            PYRSISCV_FUNCT3_OP_IMM_OP.XOR  : operator.xor,
            PYRSISCV_FUNCT3_OP_IMM_OP.OR   : operator.or_,
            PYRSISCV_FUNCT3_OP_IMM_OP.AND  : operator.and_,
            PYRSISCV_FUNCT3_OP_IMM_OP.SLT  : self.slt,  
            PYRSISCV_FUNCT3_OP_IMM_OP.SLTU : self.sltu,
            PYRSISCV_FUNCT3_OP_IMM_OP.SLL  : self.sll,
            PYRSISCV_FUNCT3_OP_IMM_OP.SRL  : self.srl,
            PYRSISCV_FUNCT3_OP_IMM_OP.SRA  : self.sra,
            PYRSISCV_FUNCT3_BRANCH.BEQ     : self.beq,
            PYRSISCV_FUNCT3_BRANCH.BNE     : self.bne,
            PYRSISCV_FUNCT3_BRANCH.BLT     : self.blt,
            PYRSISCV_FUNCT3_BRANCH.BLTU    : self.bltu,
            PYRSISCV_FUNCT3_BRANCH.BGE     : self.bge,
            PYRSISCV_FUNCT3_BRANCH.BGEU    : self.bgeu,            
        }        
        
    def __call__(self,funct3,*args):
        return self._exec_map[funct3](*args)

    def signed(self,x):
        bw = self._bw
        if x & (1<<(bw-1)):
            return -1*((1<<bw) - x)
        return x
    
    def unsigned(self,x):
        bw = self._bw
        if x > 0:
            return x
        else:
            return (1<<bw) + x
    
    def limit(self,x):
        bw = self._bw
        if -1*(1<<(bw-1)) <= x <= ((1<<(bw-1))-1):
            return x
        if x < 0:
            bwx = len(bin(x)) - 3 # -0b
            x = (1<<bwx) + x
        x = x & ((1<<bw)-1)    
        return self.signed(x)
        
    def slt(self,a,b):
        return 1 if a < b else 0

    def sltu(self,a,b):
        return 1 if self.unsigned(a) < self.unsigned(b) else 0
        
    def add(self,a,b):
        return self.limit(a+b)

    def sub(self,a,b):
        return self.limit(a-b)
    
    def sll(self,a,b):
        b = self.unsigned(b)
        shamt = b & 0x1F
        return self.limit(a<<b)
    
    def sra(self,a,b):
        b = self.unsigned(b)
        shamt = b & 0x1F
        return self.limit(a>>b)    
    
    def srl(self,a,b):
        b = self.unsigned(b)
        shamt = b & 0x1F
        a = self.unsigned(a)
        return self.limit(a>>b) 
    
    def beq(self,a,b):
        return a == b
    
    def bne(self,a,b):
        return a != b    
    
    def blt(self,a,b):
        return a < b
    
    def bltu(self,a,b):
        return self.unsigned(a) < self.unsigned(b)
    
    def bge(self,a,b):
        return a > b
    
    def bgeu(self,a,b):
        return self.unsigned(a) > self.unsigned(b)    