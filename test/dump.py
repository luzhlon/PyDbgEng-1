
from PyDbgEng.windows.core import DumpFileOpener
from PyDbgEng.windows.core.PyDbgEng import *

class Outputer(IDebugOutputCallbacksSink):
    def Output(self, this, mask, text):
        print(text.decode())

filepath = r'D:\58_588892_23207c3e_Thread15004-5DC2253C-2019-03-11-14-34-44.dmp'
filepath = filepath.encode('gbk')
dbg = DumpFileOpener.DumpFileOpener(filepath, dbg_eng_dll_path = r'D:\Debuggers\x64', output_callbacks_sink = Outputer())

# qrun.vim@any: ipython3 -i %
