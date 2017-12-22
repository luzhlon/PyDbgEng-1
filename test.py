from PyDbgEng.windows import *
dbg = UserDebugger()
dbg.run("C:/Program Files (x86)/Internet Explorer/iexplore.exe")
print(dbg.crash_name)
print(dbg.crash_description)