import sys, os.path
src = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
+ '/src/')
sys.path.append(src)
import src.process_parallel