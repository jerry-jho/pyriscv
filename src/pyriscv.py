from pymem import PyMEM
from pyriscv_regs import PyRiscvRegs
from pyriscv_types import *    
from pyriscv_riscv_def import *   
from pyriscv_operator import *
import time  
import serial 
import copy
usemc = 0
S = 0
screenread = open(r'C:/Users/Steven/Desktop/riscv/riscvgcc/pyriscv/app/app1.lst','r').read().split('\n')[-2]
screenstart = int('0x'+screenread[1:4].strip(),16)+4
print('screenstart:',screenstart)
port = 'COM1'
ser = serial.Serial(port)
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
        cur = copy.deepcopy(self._imem[screenstart])
        while not self._exit:
            S += 1
            print('next step',S)
            step = terminal(step,self._imem,self._regs)
            if cur != self._imem[screenstart]:
                if cur >= 32 and cur <= 127:
                    cur = self._imem[screenstart]
                    by = bytes(str(chr(cur)), encoding = "utf8")
                    print('cur:',cur)
                    ser.write(by)
            print("PC:",'%#x'%self._pc)
            #sp = self._regs[2]
            #print('sp:','%#x'%sp)
            #print('stacktop:','%#x'%self._imem[sp],'%#x'%self._imem[sp+1],'%#x'%self._imem[sp+2],'%#x'%self._imem[sp+3])
            if self._pc > 0xc0:
                pass
            if usemc == 1:
                setpc(val2str(self._pc))
                runningreds(self._pc)
            inst = self.__stage_if(self._pc)
            op=self._imem[self._pc] + (self._imem[self._pc+1] << 8) +  (self._imem[self._pc+2] << 16) + (self._imem[self._pc+3] << 24)
            if usemc == 1:
                setop(val2str(op))
                showreg(self._regs._regs)

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
            
            #打印c语言里的screen变量开始的视频缓冲区，内容用点阵表示

            line=""
            i=0
            for scraddr in range(screenstart,screenstart+4*4*32):
                x=self._dmem[scraddr]
                line+=format(x, "b").zfill(8)
                if i%16==15:
                    print(line)
                    line=""
                i+=1
            
            if ((self.screencnt)%4)==0:
                #将视频缓冲区内容设置到我的世界方块
                screen32val=[]
                for scraddr in range(screenstart,screenstart+4*4*32,4):     
                    x=self._dmem[scraddr]+(self._dmem[scraddr+1]<<8)+(self._dmem[scraddr+2]<<16)+(self._dmem[scraddr+3]<<24)
                    screen32val.append(x)
                if usemc == 1:
                    setscreen32mem(screen32val)
                    showscreen()
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
    

from mcpi.minecraft import Minecraft
import time
import random
import sys
maxtxtaddr=0

xG=2059
yG=49
zG=6904

x1=xG+20
y1=yG+23
z1=zG+40

list1=[41,57]
memsize=512
pagesize=128
if usemc == 1:
    mc=Minecraft.create()
    #mc=Minecraft.create("192.168.3.189",4711)
    pos=mc.player.getTilePos()
    print("player pos is",pos)
#mc.player.setTilePos(x0,y0,z0)
print("done")
stayed_time=0
pagesize=128

x0=xG+150
y0=yG
z0=zG+10

#vstr是字符串
#在cpu的右上角的操作码指令inst存储器位置设置对应方块
def setop(vstr):
    y=y1+1
    zu=z1+2
    for i in range(32):
        x=x1+i+65
        if vstr[i]=="1":
            mc.setBlock(x,y,zu,41)
        else:
            mc.setBlock(x,y,zu,57)

#vstr是字符串
#在cpu的右上角的操作码指令pc存储器位置设置对应方块
def setpc(bb):
    print("shsjxnjd",bb)
    for u in range(32):
        if bb[u]=="1":
            mc.setBlock(x1+65+u,y1+1,z1+96,41)
        else:
            mc.setBlock(x1+65+u,y1+1,z1+96,57)

def showreg(regs):
    print("regs",regs)
    for p in range(32):
        uu=val2str(regs[0+p])
        for t in range(32):
            if uu[t]=="1":
                mc.setBlock(x1+1+t,y1+1,z1+2+p,41)
            else:
                mc.setBlock(x1+1+t,y1+1,z1+2+p,57)
def setscreen32mem(sc32m):
    addrstart=screenstart//4
    for i in range(len(sc32m)):
        addr=addrstart+i
        setmem(addr,sc32m[i])

def setmem(address,value):
    bb=val2str(value)
    page=address//pagesize
    line=address%pagesize
    y=y0+23-page*8
    z=z0+line
    for i in range(32):
        x=x0+i
        if bb[i]=="1":
            mc.setBlock(x,y,z,41)
        elif bb[i]=="0":
            mc.setBlock(x,y,z,57)
        else:
            mc.setBlock(x,y,z,1)
def getmem(address):
    page=address//pagesize
    line=address%pagesize
    res=""
    for i in range(32):
        x=x0+i
        y=y0+23-page*8
        z=z0+line
        id=mc.getBlock(x,y,z)
        #print("read",x,y,z,id)
        if id==57:
            res+="0"
        elif id==41:
            res+="1"
        else:
            res+="x"
    return res
def showscreen():
    xxx=x0-96
    yyy=y0+62
    zzz=z0-5
    pixx4=""
    for addr in range(screenstart//4,screenstart//4+32):
        pixx=getmem(addr)
        pixxr=""
        for i in range(1,len(pixx)+1):
            pixxr+=pixx[-i]
        pixx4+=pixxr
        addrif=addr-35
        line=addrif//4
    
        if addrif%4==3:
            print(pixx4)
            for i in range(32*4):
                if pixx4[i]=="1":
                    mc.setBlock(xxx+i,yyy-line,zzz,41)
                
                elif pixx4[i]=="0":
                    mc.setBlock(xxx+i,yyy-line,zzz,57)
                else:
                    mc.setBlock(xxx+i,yyy-line,zzz,1)
            pixx4=""

    


#得到主存储器里pc对应的内容
#addr=pc//4
#mstr=getmem(addr)
#print("addr:",addr)
#print(mstr)

def cpy(xG,yG,zG):
    x3=x1+16
    y3=y1+2
    z3=z1+34

    #造cpu中间连接红石
    for t in range(6):
        for x in range(11):
            mc.setBlock(x3,y3-1,z3+x+10*t,1)
            mc.setBlock(x3,y3,z3+x+10*t,55,)
            mc.setBlock(x3+1,y3-1,z3+x+10*t,1)
            mc.setBlock(x3+1,y3,z3+x+10*t,93,1)#1为中继器方向
            mc.setBlock(x3+2,y3,z3+x+10*t,123)
    for t in range(6):
        mc.setBlock(x3,y3,z3+x+10*t+1,93,0)
    for t in range(4):
        for x in range(17):
            mc.setBlock(x3+x+10*t+2,y3-1,z3+62,1)
            mc.setBlock(x3+x+10*t+2,y3,z3+62,55)
            mc.setBlock(x3+x+10*t+2,y3-1,z3+61,1)
            mc.setBlock(x3+x+10*t+2,y3,z3+61,93,0)
            mc.setBlock(x3+x+10*t+2,y3,z3+60,123)
    for t in range(4):
        mc.setBlock(x3+x+10*t+2,y3,z3+62,93,1)
    mc.setBlocks(x3,y3-1,z3+62,x3+1,y3-1,z3+61,7)
    mc.setBlocks(x3,y3,z3+62,x3+1,y3,z3+61,55)
    mc.setBlock(x3+1,y3,z3+62,93,1)

    for t1 in range(3):
        for x9 in range(11):
            mc.setBlock(x1+34+x9+10*t1,y1+1,z1+2,1)
            mc.setBlock(x1+34+x9+10*t1,y1+2,z1+2,55)
            mc.setBlock(x1+34+x9+10*t1,y1+1,z1+3,1)
            mc.setBlock(x1+34+x9+10*t1,y1+2,z1+3,93,2)
            mc.setBlock(x1+34+x9+10*t1,y1+2,z1+4,123)
    for t5 in range(3):
        mc.setBlock(x1+34+x9+5*t1,y1+2,z1+2,93,1)
    for t2 in range(2):
        for x8 in range(17):
            mc.setBlock(x1+79,y1+1,z1+4+x8+10*t2,1)
            mc.setBlock(x1+79,y1+2,z1+4+x8+10*t2,55)
            mc.setBlock(x1+78,y1+1,z1+4+x8+10*t2,1)
            mc.setBlock(x1+78,y1+2,z1+4+x8+10*t2,93,3)
            mc.setBlock(x1+77,y1+2,z1+4+x8+10*t2,123)
    for t3 in range(3):
        for x7 in range(13):
            mc.setBlock(x1+79,y1+1,z1+63+x7+10*t3,1)
            mc.setBlock(x1+79,y1+2,z1+63+x7+10*t3,55)
            mc.setBlock(x1+78,y1+1,z1+63+x7+10*t3,1)
            mc.setBlock(x1+78,y1+2,z1+63+x7+10*t3,93,3)
            mc.setBlock(x1+77,y1+2,z1+63+x7+10*t3,123)
        #造围墙        
    for q in range(5):
        for i9 in range(98):
            mc.setBlock(x1+i9,y1+q,z1,89)
        for t in range(99):
            mc.setBlock(x1+i9,y1+q,z1+t,89)
        for p in range(98):
            mc.setBlock(x1+i9-p,y1+q,z1+t,89)
        for z in range(99):
            mc.setBlock(x1+i9-p,y1+q,z1+t-z,89)
        #造地板
    for e in range(98):
        for v in range(99):
            mc.setBlock(x1+i9-p+e,y1,z1+t-z+v,42)
            mc.setBlock(x1+i9-p+e,y1-1,z1+t-z+v,42)
       #随机寄存器     
    for o8 in range(32):
        for o6 in range(16):
            a=random.sample(list1,1)
            mc.setBlock(x1+2+o6*2,y1+1,z1+33-o8,a)        
        for o7 in range(16):
            a=random.sample(list1,1)
            mc.setBlock(x1+1+o7*2,y1+1,z1+33-o8,a)
    for o9 in range(16):
            a=random.sample(list1,1)
            mc.setBlock(x1+96-o9*2,y1+1,z1+2,a)
    for o10 in range(16):
            a=random.sample(list1,1)
            mc.setBlock(x1+95-o10*2,y1+1,z1+2,a)        
    for o11 in range(16):
            a=random.sample(list1,1)
            mc.setBlock(x1+96-o11*2,y1+1,z1+3,a)
    for o12 in range(16):
            a=random.sample(list1,1)
            mc.setBlock(x1+95-o12*2,y1+1,z1+3,a)
    #造蓝色alu
    for z in range(32):
        for z2 in range(32):
            mc.setBlock(x1+65+z,y1+1,z1+31+z2,22)
    #中间地板换材质
    for o14 in range(96):
        for o13 in range(32):
                mc.setBlock(x1+33+o13,y1,z1+1+o14,25)
    

    #随机pc
    for o15 in range(16):
            a=random.sample(list1,1)    
            mc.setBlock(x1+96-o15*2,y1+1,z1+96,a[0])
    for o16 in range(16):
            a=random.sample(list1,1)    
            mc.setBlock(x1+95-o16*2,y1+1,z1+96,a[0])

def setoutmem(address):
    bb=getmem(address)
    page=address//pagesize
    line=address%pagesize
    y=y0+23-page*8
    z=z0+line
    for i in range(32):
        x=x0-1-i-1
        if bb[i]=="1":
            mc.setBlock(x,y,z,41)
        elif bb[i]=="0":
            mc.setBlock(x,y,z,57)
        else:
            mc.setBlock(x,y,z,10)
#消除外条
def rmoutmem(address):
    bb=getmem(address)
    page=address//pagesize
    line=address%pagesize
    y=y0+23-page*8
    z=z0+line
    for i in range(32):
        x=x0-1-i-1
        if bb[i]=="1":
            mc.setBlock(x,y,z,0)
        else:
            mc.setBlock(x,y,z,0)

#消除老的外条
#显示新的现在的红石
def runningreds(pc):
    addrpc=pc//4
    numaddrpc=int(addrpc)
    y=addrpc//pagesize
    z=addrpc%pagesize
    setoutmem(addrpc)
    rmoutmem(addrpc)
    #单个红石头以及加墨亮红石的石头
    mc.setBlock(x0-1,y0+27-y,z0+z,152)
    time.sleep(1)
    mc.setBlock(x0-1,y0+27-y,z0+z,0)
    mc.setBlock(x0-2,y0+25,z0+1,152)
    mc.setBlock(xG+144,yG+25,zG+7,152)
    time.sleep(0.01)
    mc.setBlock(x0-2,y0+25,z0+1,0)
    mc.setBlock(xG+144,yG+25,zG+7,0)
            
def bridge(q0,t0,w0,q1,w1,e0):
    q2=abs(q1-q0)
    w2=abs(w1-w0)
    
    if e0==1:
        if q1-q0>0:
            if w1-w0>0:
                print("1")
                for t in range(q2):
                        mc.setBlock(q0+t+1,t0-1,w0-2,1)
                        mc.setBlock(q0+t+1,t0,w0-2,55,)
                        mc.setBlock(q0+t+1,t0-1,w0-1,1)
                        mc.setBlock(q0+t+1,t0,w0-1,93)
                        mc.setBlock(q0+t+1,t0,w0,123)
                        mc.setBlock(pos.x+x+10*t+1,pos.y,pos.z,93,1)
                for t1 in range(w2):
                        mc.setBlock(q0+q2+2,t0-1,w0+t1,1)
                        mc.setBlock(q0+q2+2,t0,w0+t1,55,)
                        mc.setBlock(q0+q2+1,t0-1,w0+t1,1)
                        mc.setBlock(q0+q2+1,t0,w0+t1,93)
                        mc.setBlock(q0+q2,t0,w0+t1,123)
                mc.setBlocks(q0+q2+1,t0-1,w0-2,q0+q2+2,t0-1,w0-1,7)
                mc.setBlocks(q0+q2+1,t0,w0-2,q0+q2+2,t0,w0-1,55)
                mc.setBlock(q0+q2+1,t0,w0-2,93,3)
                
            if w1-w0<0:
                print("2")
                for t in range(q2+2):
                        mc.setBlock(q0+t,t0-1,w0,1)
                        mc.setBlock(q0+t,t0,w0,55,)
                        mc.setBlock(q0+t,t0-1,w0-1,1)
                        mc.setBlock(q0+t,t0,w0-1,93)
                        mc.setBlock(q0+t,t0,w0-2,123)
                for t2 in range(5):
                        mc.setBlock(q0+5*t2,t0,w0,93,3)
                for t1 in range(w2+2):
                        mc.setBlock(q0+q2+2,t0-1,w0-t1-2,1)
                        mc.setBlock(q0+q2+2,t0,w0-t1-2,55,)
                        mc.setBlock(q0+q2+1,t0-1,w0-t1-2,1)
                        mc.setBlock(q0+q2+1,t0,w0-t1-2,93,3)
                        mc.setBlock(q0+q2,t0,w0-t1-2,123)
                for t2 in range(7):
                        mc.setBlock(q0+q2+2,t0,w0-t2*5,93,2)        
                mc.setBlocks(q0+q2+1,t0-1,w0-1,q0+q2+2,t0-1,w0,7)
                mc.setBlocks(q0+q2+1,t0,w0-1,q0+q2+2,t0,w0,55)
                mc.setBlock(q0+q2+1,t0,w0,93,3)
        if q1-q0<0:
            if w1-w0>0:
                print("3")
                for t in range(q2):
                        mc.setBlock(q0-t,t0-1,w0-2,1)
                        mc.setBlock(q0-t,t0,w0-2,55,)
                        mc.setBlock(q0-t,t0-1,w0-1,1)
                        mc.setBlock(q0-t,t0,w0-1,93,2)
                        mc.setBlock(q0-t,t0,w0,123)
                for t1 in range(w2):
                        mc.setBlock(q0-t,t0-1,w0+t1,1)
                        mc.setBlock(q0-t,t0,w0+t1,55,)
                        mc.setBlock(q0-t+1,t0-1,w0+t1,1)
                        mc.setBlock(q0-t+1,t0,w0+t1,93,1)
                        mc.setBlock(q0-t+2,t0,w0+t1,123)
                mc.setBlocks(q0-t,t0-1,w0-2,q0-t+1,t0-1,w0-1,7)
                mc.setBlocks(q0-t,t0,w0-2,q0-t+1,t0,w0-1,55)
                mc.setBlock(q0-t,t0,w0-1,93,2)
            if w1-w0<0:
                print("4")
                for t in range(q2):
                        mc.setBlock(q0-t-1,t0-1,w0,1)
                        mc.setBlock(q0-t-1,t0,w0,55,)
                        mc.setBlock(q0-t-1,t0-1,w0-1,1)
                        mc.setBlock(q0-t-1,t0,w0-1,93,0)
                        mc.setBlock(q0-t-1,t0,w0-2,123)
                for t1 in range(w2):
                        mc.setBlock(q0-t-1,t0-1,w0-t1-2,1)
                        mc.setBlock(q0-t-1,t0,w0-t1-2,55,)
                        mc.setBlock(q0-t,t0-1,w0-t1-2,1)
                        mc.setBlock(q0-t,t0,w0-t1-2,93,1)
                        mc.setBlock(q0-t+1,t0,w0-t1-2,123)

    mc.setBlocks(xG+150-5,y1+1,zG+10-1,xG+150-2,y1+1,zG+10,7)
    mc.setBlocks(xG+150-5,y1+2,zG+10,xG+150-2,y1+2,zG+10,55)
    mc.setBlock(xG+150-6,y1+2,zG+10,123)
    mc.setBlock(xG+150-6,y1+2,zG+10-1,123)
    mc.setBlocks(xG+150-6,y1+2,zG+10-2,xG+150-2,y1+2,zG+10-2,123)
    mc.setBlocks(xG+150-5,y1+2,zG+10,xG+150-5,y1+2,zG+10-1,93,3)
    mc.setBlocks(xG+150-4,y1+2,zG+10-1,xG+150-2,y1+2,zG+10-1,93,0)           

def creatFrame(memsize,pagesize):
    pagenumber=memsize//pagesize
    #底座
    for h in range(pagenumber):
        mc.setBlocks(x0-1,y0-1+h*8,z0,x0+33,y0-1+h*8,z0+pagesize,1)
    #底座是一大块实心石头，清除多余部分
    for hh in range(pagenumber):
        mc.setBlocks(x0,y0+3+h*6,z0+1,x0+33,y0+4+h*6,z0+pagesize,0)
    #墙
    for h in range(pagenumber):
        for i in range(32+2):
            for m in range(pagesize+2):
                for n in range(3):
                    mc.setBlock(x0-1+i,y0+n+h*8,z0-1,42)
                    mc.setBlock(x0-1,y0+n+h*8,z0-1+m,89)
                    mc.setBlock(x0-1+i,y0+n+h*8,z0-1+pagesize+1,89)
                    mc.setBlock(x0-1+33,y0+n+h*8,z0-1+m,89)
if usemc == 1:
    creatFrame(512,128)
    bridge(x1+98,y1+2,z1+2,xG+180-6-30,zG+10+4,1)
    cpy(xG,yG,zG)

        
print(sys.path[0])
imem = PyMEM(sys.path[0]+'/../app/app1.mem')
cnt=0
for a in imem.keys():
    cnt+=1
    #print("%#x"%a,a,"%#x"%imem[a])

if usemc == 1:
    for i in range(0,cnt,4):
        x=imem[i]+(imem[i+1]<<8)+(imem[i+2]<<16)+(imem[i+3]<<24)
        setmem(i//4,x)
    
PyRiscv(imem,imem)
