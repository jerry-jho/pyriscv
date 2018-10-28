# PYMEM
# Author: jerry-jho@github

from collections import OrderedDict

class PyMEM:
    FORMAT_VLOG_B8 = 1
    
    def __init__(self,file_or_fileobj,FORMAT=None):
        obj_close_flag = type(file_or_fileobj) == type("")
        if obj_close_flag:
            file_or_fileobj = open(file_or_fileobj,"r")
        self._mdata = OrderedDict()   
        if FORMAT is None:
            self.__read_vlog_b8(self._mdata, file_or_fileobj)
        if obj_close_flag:
            file_or_fileobj.close()
                
    def __read_vlog_b8(self,mdata,fileobj):
        addr = 0
        for line in fileobj:
            segs = line.strip().split(' ')
            for seg in segs:
                if seg == '':
                    continue
                if seg.startswith('@'):
                    addr = int(seg[1:],base=16)
                else:
                    data = int(seg,base=16)
                    mdata[addr] = data
                    addr += 1
    def __getitem__(self,addr):
        return self._mdata[addr]
    def __setitem__(self,addr,data):
        self._mdata[addr] = data
                    
if __name__ == '__main__':
    import sys
    o = PyMEM(sys.argv[1])
    print(o._mdata)
        