from lispy.interpreter import Interpreter
from lispy.interpreter.loader import FileSysLoader
import os, sys


cwd = os.getcwd()
loader = FileSysLoader([cwd])
interp = Interpreter(loader)
result = interp.run_module(sys.argv[1])
