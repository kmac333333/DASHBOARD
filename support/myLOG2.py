# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 15:02:13 2022

@author: k
"""
import logging
import threading
import inspect

from support.term_color import (ci_green, ci_blue, ci_grey, ci_light_blue,
            ci_purple, ci_yellow, ci_red, ci_cyan, co, _G,G_, _BW,BW_,
            c_bold_on, c_bold_off)

from support.term_color import cize


# ==============================================================================
# logging
# ==============================================================================
formatter = "{asctime}.{msecs:0<3.0f} {qthreadName} {message}"
logging.basicConfig(
    format=formatter, datefmt="%H:%M:%S", level=logging.DEBUG, style="{"
)
def ctname():
    return threading.current_thread().name

def LOG2(s):
    extras = {"qthreadName": f"{ctname():<11s}"}
    s = f"{fname2():<19s}: {s}"
    logging.info(s, extra=extras)
   
def to_hex(self,data):
    return ":".join("{:02x}".format(c) for c in data)

def fname2():            # callers function name
    return f"{c_bold_on}{inspect.stack()[2][3]:<28s}{c_bold_off}"

def LOG3(n:int,f:str):
    s = f"{cize(n)} "
    s = f"{s}: " + f
    
    extras = {"qthreadName": f"{ctname():<11s}"}
    s = f"{fname2():<19s}: {s}"
    logging.info(s, extra=extras)
    
    
    
    