# About

PyDbgEng is a python wrapper of debug engines on windows, linux or osx, it's only aim to auto fuzzing.

It's easy to use:

```Python
from PyDbgEng.windows import *
dbg = UserDebugger()
dbg.run("C:/Program Files (x86)/Internet Explorer/iexplore.exe")
print(dbg.crash_name)
print(dbg.crash_description)
```

You will get `dbg.crash_name` like this:
```Bash
PROBABLY_NOT_EXPLOITABLE_ReadAVNearNull_0x76da4b51_0x429cab36
```

and `dbg.crash_description` like this:
```Bash
> r
rax=000061bee3327a7a rbx=0000000000000000 rcx=0000000005c99dc0
rdx=0000000005c99db0 rsi=000000000b05ed08 rdi=0000000005c99dc0
rip=000007feee0f07dd rsp=0000000005c99ca0 rbp=0000000005c99d10
cs=0033  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00010246
MSHTML!CreateCoreWebView+0x7074d:
000007fe`ee0f07dd 4439b39c000000  cmp     dword ptr [rbx+9Ch],r14d ds:00000000`0000009c=????????
> !exploitable -m
INSTRUCTION_ADDRESS:0x000007fabd1c96e1
INVOKING_STACK_FRAME:0
DESCRIPTION:Read Access Violation near NULL
SHORT_DESCRIPTION:ReadAVNearNull
CLASSIFICATION:PROBABLY_NOT_EXPLOITABLE
BUG_TITLE:Read Access Violation near NULL starting at MSHTML!DllCanUnloadNow+0x01
Hash=0x76da4b51.0x429cab36
EXPLANATION:This is a user mode read access violation near null, and is probably not exploitable.
```

# Features

* The automated monitoring module specially developed for Fuzzing.
* Support Exploitable plugin to determine the crash is exploitable or not.
* Support for Windows, linux and Mac OS.

# Requirements

* Required
	* comtypes

# Attentions

When target process is multiprocess like chrome and IE, you should set 
function dbg.run 's follow_forks argument to True, and when target process is singleprocess like firefox, you should set follow_forks to False whick is equal to Singleprocess.

# Versions

* v0.0.4 - 2017.12.22
  * remove psutil packages dependent.
  * add linux and mac os plan.
* v0.0.3
	* fix bugs when process is singleprocess or multiprocess.
* v0.0.2
	* fix bugs when comtypes.gen isn't exist.
	* add Visual C++ Redistributable 2012 setup to install steps.
* v0.0.1
	* change pydbgeng for python 3.x.

------

If you want to report bugs or suggestions, please e-mail contact walkerfuz#outlook.com.