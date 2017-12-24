import os
import sys
import re
import hashlib
import comtypes
try:
    from comtypes.gen import DbgEng
except ImportError:
    tlb = os.path.join(os.path.dirname(__file__), "utils", "DbgEng.tlb")
    comtypes.client.GetModule(tlb)
    from comtypes.gen import DbgEng
from .core import *

class DebugEventHandler(IDebugOutputCallbacksSink, IDebugEventCallbacksSink):
    def __init__(self):
        self.buffer = ''
    def Output(self, this, Mask, Text):
        try:
            Text = Text.decode()
        except:
            pass
        self.buffer += Text

    def GetInterestMask(self):
        return DbgEng.DEBUG_EVENT_EXCEPTION | DbgEng.DEBUG_FILTER_INITIAL_BREAKPOINT | DbgEng.DEBUG_EVENT_LOAD_MODULE

    def LoadModule(self, dbg, ImageFileHandle, BaseOffset, ModuleSize, ModuleName, ImageName, CheckSum, TimeDateStamp):
        return DbgEng.DEBUG_STATUS_NO_CHANGE

    def ExitProcess(self, this, ExitCode):
        self.quit.set()
        return DbgEng.DEBUG_STATUS_NO_CHANGE

    def Exception(self, dbg, ExceptionCode, ExceptionFlags, ExceptionRecord,
            ExceptionAddress, NumberParameters, ExceptionInformation0, ExceptionInformation1,
            ExceptionInformation2, ExceptionInformation3, ExceptionInformation4,
            ExceptionInformation5, ExceptionInformation6, ExceptionInformation7,
            ExceptionInformation8, ExceptionInformation9, ExceptionInformation10,
            ExceptionInformation11, ExceptionInformation12, ExceptionInformation13,
            ExceptionInformation14, FirstChance):
        if self.IgnoreSecondChanceGardPage and ExceptionCode == 0x80000001:
            return DbgEng.DEBUG_STATUS_NO_CHANGE

       # Only capture dangerouse first chance exceptions
        if FirstChance:
            if self.IgnoreFirstChanceGardPage and ExceptionCode == 0x80000001:
                # Ignore, sometimes used as anti-debugger by Adobe Flash.
                return DbgEng.DEBUG_STATUS_NO_CHANGE
            elif ExceptionCode == 0x80000001 or ExceptionCode == 0xC000001D:
                # Guard page or illegal op
                pass
            elif ExceptionCode == 0xC0000005:
                if ExceptionInformation0 == 0 and ExceptionInformation1 == ExceptionAddress: # is av on eip or not
                    pass
                elif ExceptionInformation0 == 1 and ExceptionInformation1 != 0: # is write a/v or not
                    pass
                elif ExceptionInformation0 == 0: # is DEP or not
                    pass
                else:
                    # Otherwise skip first chance
                    return DbgEng.DEBUG_STATUS_NO_CHANGE
            else:
                # otherwise skip first chance
                return DbgEng.DEBUG_STATUS_NO_CHANGE

        if self.handlingFault.is_set() or self.handledFault.is_set():
            # We are already handling, so skip
            return DbgEng.DEBUG_STATUS_BREAK
        # Crash is occured.
        self.buffer = ''
        self.handlingFault.set()

        ## 1. Output registers
        dbg.idebug_control.Execute(DbgEng.DEBUG_OUTCTL_THIS_CLIENT,
                                   c_char_p(b"r"),
                                   DbgEng.DEBUG_EXECUTE_ECHO)
        self.buffer += "\n"

        ## 2. Ouput stack trace
        if DebugEventHandler.TakeStackTrace:
            #print("Exception: 2. Output stack trace")
            dbg.idebug_control.Execute(DbgEng.DEBUG_OUTCTL_THIS_CLIENT,
                                       c_char_p(b"k"),
                                       DbgEng.DEBUG_EXECUTE_ECHO)
        else:
            DebugEventHandler.TakeStackTrace = True
            self.buffer += "[Exception]: Error, stack trace failed."
        self.buffer += "\n"

        ## 3. Write dump file
        minidump = None
        ## 4. Bang-Exploitable
        try:
            if sys.version.find("AMD64") != -1:
                p = os.path.join(os.path.dirname(__file__), "utils", 'x64', 'MSEC.dll')
            else:
                p = os.path.join(os.path.dirname(__file__), "utils", 'x86', 'MSEC.dll')
            p = ".load {}".format(p)
            dbg.idebug_control.Execute(DbgEng.DEBUG_OUTCTL_THIS_CLIENT, c_char_p(p.encode(encoding="utf-8")), DbgEng.DEBUG_EXECUTE_ECHO)
            dbg.idebug_control.Execute(DbgEng.DEBUG_OUTCTL_THIS_CLIENT, c_char_p(b"!exploitable -m"), DbgEng.DEBUG_EXECUTE_ECHO)

            majorHash = re.compile("^MAJOR_HASH:(0x.*)$", re.M).search(self.buff).group(1)
            classification = re.compile("^CLASSIFICATION:(.*)$", re.M).search(self.buff).group(1)
            shortDescription = re.compile("^SHORT_DESCRIPTION:(.*)$", re.M).search(self.buff).group(1)
            bucket = "{}_{}_{}".format(classification, shortDescription, majorHash)

        except:
            self.buffer += "[Exception]: Load exploitalbe MSEC.dll failed."
            self.buffer += "\n"
            x = (ExceptionCode, ExceptionFlags, ExceptionRecord,
                    ExceptionAddress, NumberParameters, ExceptionInformation0, ExceptionInformation1,
                    ExceptionInformation2, ExceptionInformation3, ExceptionInformation4,
                    ExceptionInformation5, ExceptionInformation6, ExceptionInformation7,
                    ExceptionInformation8, ExceptionInformation9, ExceptionInformation10,
                    ExceptionInformation11, ExceptionInformation12, ExceptionInformation13,
                    ExceptionInformation14, FirstChance)
            h = hashlib.md5()
            h.update((''.join([str(item) for item in list(x)])).encode(encoding='utf-8'))
            bucket = "Unknown_%s" % (h.hexdigest())

        self.crash_name = bucket
        self.crash_description = self.buffer
        self.fault = True
        # IDebugClient::TerminateProcesses
        self.dbg.TerminateProcesses()

        self.handledFault.set()
        return DbgEng.DEBUG_STATUS_GO
