from PyDbgEng.windows import *
dbg = UserDebugger()
dbg.run("C:/Program Files/Internet Explorer/iexplore.exe http://127.0.0.1")
print(dbg.crash_name)
print(dbg.crash_description)