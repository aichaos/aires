#!/usr/bin/env python

"""Aires Bot"""

import os
import sys

# Add the source folder to the python search path
sys.path.append('./src')

from aires import Aires

def main():
    bot = Aires()
    bot.init()
    bot.run()

if __name__ == "__main__":
    main()
