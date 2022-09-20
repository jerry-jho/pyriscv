from pyriscv_operator import *

class PyRiscvRegs:
    def __init__(self,n,bw):
        self._regs = [0] * n
        self._bw = bw
        
    def __getitem__(self,a):
        if a == 0:
            return 0
        
        return self._regs[a]
    
    def __setitem__(self,a,v):
        fmt = '0%dx' % (self._bw / 4)
        fmt = '%' + fmt
        hv = fmt % v
        if a == 0:
            print("[DEBUG] 0x%s(%d)" % (hv,v))
        else:               
            
            #print("X%d <= %d(%x)" % (a,v,v))
            self._regs[a] = v