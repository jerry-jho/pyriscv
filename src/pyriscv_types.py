from enum import Enum
import argparse

class PyRiscvStruct(argparse.Namespace):
    pass

class PyRiscvEnum(Enum):
    def __repr__(self):
        return self.__class__.__name__ + '.' + self.name
    @classmethod
    def FV(cls,v):
        try:
            return cls(v)
        except:
            #print(v)
            return None
        
class PyRiscvLogic:
    def __init__(self,d):
        self._d = d
    
    def __int__(self):
        return self._d
    
    def __hex__(self):
        return hex(self._d)
    
    def __getitem__(self,s):
        if isinstance(s,slice):
            return (((self._d >> (s.start + 1)) << (s.start + 1)) ^ self._d) >> s.stop
        else:
            return (0x1 & (self._d >> s))