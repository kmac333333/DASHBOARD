# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 06:30:36 2022

@author: k

https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797

"""

# color stuff - formalize later
ci_grey = "\x1b[38;21m"
ci_blue = "\x1b[1;34m"
ci_light_blue = "\x1b[1;36m"
ci_purple = '\x1b[35;1m'
ci_red = '\x1b[31;1m'
ci_yellow = '\x1b[33;1m'
ci_green = '\x1b[32;1m'
ci_cyan = '\x1b[36;1m'
ci_a = '\x1b[35;1m'
c_bold_on = '\x1b[1m'
c_bold_off = '\x1b[0m'
ci_blk_on_w = '\x1b[38;5;232m' + '\x1b[48;5;231m'
ci_red_on_w = '\x1b[38;5;196m' + '\x1b[48;5;236m'
co = '\x1b[0m'

_R = ci_red
R_ = co
_B = ci_blue
B_ = co
_Y = ci_yellow
Y_ = co
_G = ci_green
G_ = co
OFF = co
_BW = ci_blk_on_w
BW_ = co

c = {
     0 : ci_green,
     100 : ci_blue,
     200 : ci_yellow,
     300 : ci_light_blue,
     400 : ci_purple,
     500 : ci_yellow,
     600 : ci_cyan,
     700 : ci_light_blue,
     800 : ci_grey,
     900 : ci_red,
     1000 : ci_red,
     1100 : ci_blk_on_w,
     1600 : ci_red_on_w
    }

def cize(N:int)->str :
    s = f"{c[find_interval_key(c,N)]}{N:<4d}{co}" 
    return  s

def find_interval_key(brackets: dict[int, any], target: int)->int:
    """
    Returns the key such that key <= target < next_key.
    Returns None if target is below the smallest key.
    """
    candidate_key = None
    for key in brackets:
        if key <= target:
            candidate_key = key  # This key is a possible lower bound
        else:
            # We've gone past target → previous key was the one
            return candidate_key
    # If we finish the loop, target is in the last (highest) interval
    return candidate_key

# =============================================================================
# M A I N
# =============================================================================
def main():
    print(f"{cize(1)} : done")
    print(f"{cize(101)} : done")
    print(f"{cize(201)} : done")
    print(f"{cize(301)} : done")
    print(f"{cize(401)} : done")
    print(f"{cize(501)} : done")
    print(f"{cize(601)} : done")
    print(f"{cize(701)} : done")
    print(f"{cize(801)} : done")
    print(f"{cize(901)} : done")
    print(f"{cize(1001)} : done")
    print(f"{cize(1100)} : done")
# =============================================================================
# S T A R T
# ============================================================================= 
if __name__ == '__main__':
        main()
        
        
   
