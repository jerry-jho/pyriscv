from pymem import PyMEM
from pyriscv_regs import PyRiscvRegs
from pyriscv_types import *    
from pyriscv_riscv_def import *   
from pyriscv_operator import *
import time  
import serial 
import copy
S = 0
usescr = 1
screenread = open(r'D:\Desktop/IB/Project/riscvgcc/pyriscv/app/app1.lst','r').read().split('\n')[-2]
print(screenread)
screenstart = int('0x'+screenread[1:4].strip(),16)+4
print('screenstart:',screenstart)
'''
port = 'COM1'
ser = serial.Serial(port)
'''
maxtxtaddr = 0
def terminal(s,mem,regs):
    if s == 0:
        n = input()
        if n == '':
            terminal(s,mem,regs)
        else:
            if n == 'g':
                s = 1000
            elif n[0] == 'g' and n != 'g':
                s = int(n[1:])
            elif n == 's':
                s = 1
            elif n[0] == 'd':
                t = (int(n[1:])//16) * 16
                ln = "%04X"%t + ':'
                for i in range(t,t+16):
                    ln += "%02X"%mem[i]+' '
                print(ln)
                t += 16
                ln = "%04X"%t + ':'
                for i in range(t,t+16):
                    ln += "%02X"%mem[i]+' '
                ln += '\n'
                print(ln)
                s += 1
            elif n[0] == 'r':
                print(list(regs))
    if s > 0:
        s -= 1
    return s
step = 0
def val2str(val):
    c=bin(val).replace("0b","")
    po="0"*(32-len(c))
    bb=po+c
    return bb
class PyRiscv:
    def __init__(self,imem,dmem,reset_vec=0,bw=32):
        self._imem = imem
        self._dmem = dmem
        self._pc   = reset_vec
        self._regs = PyRiscvRegs(32,bw)
        self._operator = PyRiscvOperator(bw)
        self._bw = bw
        self.screencnt=0
        self.__control()
        
    def __control(self):
        S = 0
        step = 0
        self._exit = False
        try:
            cur = copy.deepcopy(self._imem[screenstart])
        except:
            cur = 0
            screenstart = 0
        while not self._exit:
            S += 1
            print('next step',S)
            step = terminal(step,self._imem,self._regs)
            if cur != self._imem[screenstart]:
                if cur >= 32 and cur <= 127:
                    cur = self._imem[screenstart]
                    by = bytes(str(chr(cur)), encoding = "utf8")
                    print('cur:',cur)
                    'ser.write(by)'
            print("PC:",'%#x'%self._pc)
            #sp = self._regs[2]
            #print('sp:','%#x'%sp)
            #print('stacktop:','%#x'%self._imem[sp],'%#x'%self._imem[sp+1],'%#x'%self._imem[sp+2],'%#x'%self._imem[sp+3])
            if self._pc > 0xc0:
                pass
            inst = self.__stage_if(self._pc)
            op=self._imem[self._pc] + (self._imem[self._pc+1] << 8) +  (self._imem[self._pc+2] << 16) + (self._imem[self._pc+3] << 24)


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
        decode_map.FUNCT3_LOADSTORE    = PYRSISCV_FUNCT3_LOAD_STORE.FV(w[14:12])
        decode_map.FUNCT7              = w[31:25]
        decode_map.RD                  = w[11:7]
        decode_map.RS1                 = w[19:15]
        decode_map.RS2                 = w[24:20]
        decode_map.IMMJ                = PyRiscvOperator(21).signed((w[30:21]<<1) | (w[20] << 11)   | (w[19:12] << 12) | (w[31] << 20))
        decode_map.IMMB                = PyRiscvOperator(13).signed((w[11:8]<<1)  | (w[30:25] << 5) | (w[7] << 11)     | (w[31] << 12))
        decode_map.IMMI                = PyRiscvOperator(12).signed(w[31:20])
        decode_map.IMMS                = PyRiscvOperator(12).signed(w[11:7] + (w[31:25]<<5))
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
        print(decode_map.OPCODE)
        if decode_map.OPCODE == PYRSISCV_OPCODE.JAL:
            self._regs[decode_map.RD] = self._pc + 4
            self._pc += decode_map.IMMJ
        elif decode_map.OPCODE == PYRSISCV_OPCODE.JALR:
            self._regs[decode_map.RD] = self._pc + 4
            self._pc = decode_map.IMMI
            self._pc = ((self._pc + self._regs[decode_map.RS1]) | 0x1) - 1
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
            print('LUI',self._pc,self._regs[decode_map.RD],decode_map.RD,decode_map.IMMU)
            self._regs[decode_map.RD] = decode_map.IMMU
            self._pc += 4
        elif decode_map.OPCODE == PYRSISCV_OPCODE.AUIPC:
            print(decode_map.IMMU)
            self._pc += decode_map.IMMU
            self._regs[decode_map.RD] = self._pc   
        elif decode_map.OPCODE == PYRSISCV_OPCODE.LOAD:
            dmem_base = self._regs[decode_map.RS1] + decode_map.IMMI
            if decode_map.FUNCT3_LOADSTORE == PYRSISCV_FUNCT3_LOAD_STORE.W:
                self._regs[decode_map.RD] = PyRiscvOperator(self._bw).signed(self._dmem[dmem_base] + (self._dmem[dmem_base + 1] << 8) + \
                                            (self._dmem[dmem_base + 2] << 16) + (self._dmem[dmem_base + 3] << 24))
            elif decode_map.FUNCT3_LOADSTORE == PYRSISCV_FUNCT3_LOAD_STORE.H:
                self._regs[decode_map.RD] = PyRiscvOperator(16).signed(self._dmem[dmem_base] + (self._dmem[dmem_base + 1] << 8))
            elif decode_map.FUNCT3_LOADSTORE == PYRSISCV_FUNCT3_LOAD_STORE.HU:
                self._regs[decode_map.RD] = self._dmem[dmem_base] + (self._dmem[dmem_base + 1] << 8)
            elif decode_map.FUNCT3_LOADSTORE == PYRSISCV_FUNCT3_LOAD_STORE.B:
                self._regs[decode_map.RD] = PyRiscvOperator(8).signed(self._dmem[dmem_base])
            elif decode_map.FUNCT3_LOADSTORE == PYRSISCV_FUNCT3_LOAD_STORE.BU:
                self._regs[decode_map.RD] = self._dmem[dmem_base]
            self._pc += 4
        elif decode_map.OPCODE == PYRSISCV_OPCODE.STORE:
            dmem_base = self._regs[decode_map.RS1] + decode_map.IMMS
            dmem_data = PyRiscvOperator(self._bw).unsigned(self._regs[decode_map.RS2])
            print("ST addr",'%#x'%dmem_base,"val",'%#x'%dmem_data)
            i=0
            line='%#5x'%i+":"
            note=""
            #print(list(self._dmem.keys()))
            for addr in range(maxtxtaddr+1):
                x=self._dmem[addr]
                line+=str('%#5x'%x)+" "
                if ord("~")>x>ord(" "):
                    note+=chr(x)
                else:
                    note+="."
                if i%4==3:
                    print(line+" "+note)
                    line='%#5x'%(addr+1)+":"
                    note=""
                i+=1
            

            line=""
            i=0
            if usescr == 1:
                for scraddr in range(screenstart,screenstart+4*4*32):
                    x=self._dmem[scraddr]
                    line+=format(x, "b").zfill(8)
                    if i%16==15:
                        print(line)
                        line=""
                    i+=1
                
                if ((self.screencnt)%4)==0:
                    screen32val=[]
                    for scraddr in range(screenstart,screenstart+4*4*32,4):     
                        x=self._dmem[scraddr]+(self._dmem[scraddr+1]<<8)+(self._dmem[scraddr+2]<<16)+(self._dmem[scraddr+3]<<24)
                        screen32val.append(x)
                (self.screencnt)+=1
            if decode_map.FUNCT3_LOADSTORE == PYRSISCV_FUNCT3_LOAD_STORE.W:
                self._dmem[dmem_base]   = dmem_data & 0xFF
                self._dmem[dmem_base+1] = (dmem_data & 0xFF00) >> 8
                self._dmem[dmem_base+2] = (dmem_data & 0xFF0000) >> 16
                self._dmem[dmem_base+3] = (dmem_data & 0xFF000000) >> 24
            elif decode_map.FUNCT3_LOADSTORE == PYRSISCV_FUNCT3_LOAD_STORE.H:
                self._dmem[dmem_base]   = dmem_data & 0xFF
                self._dmem[dmem_base+1] = (dmem_data & 0xFF00) >> 8
            elif decode_map.FUNCT3_LOADSTORE == PYRSISCV_FUNCT3_LOAD_STORE.B:
                self._dmem[dmem_base]   = dmem_data & 0xFF
            self._pc += 4
        if decode_map.EXIT:
            self._exit = True

import sys
print(sys.path[0])
imem = PyMEM(sys.path[0]+'/../app/app1.mem')
cnt=0
for a in imem.keys():
    cnt+=1
    #print("%#x"%a,a,"%#x"%imem[a])


PyRiscv(imem,imem)
