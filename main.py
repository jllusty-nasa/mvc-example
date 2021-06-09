# Model is our program, runs in its own thread
from model import Model
# ViewController controls and views our program, runs in main thread
from viewcontrollers import CmdViewController, TkViewController

# since our model and viewcontroller are running in separate threads, we need
# to facilitate asynchronous communication between them: use queues.
from queue import Queue

# for command-line args
import sys

# entry point
def main():
    args = sys.argv
    if len(args) == 1:
        print("Please call with a particular ViewController interface, i.e. ")
        print("\t> main.py X")
        print("where X = 'cmd' or X = 'tk'")
        return

    # initialize queues
    #  controller->model queue
    cmq = Queue()
    #  model->view queue
    mvq = Queue()

    # initialize window (ViewController)
    if args[1] == 'tk':
        vc = TkViewController(cmq,mvq)
    elif args[1] == 'cmd':
        vc = CmdViewController(cmq,mvq)
    else:
        print("Unknown ViewController interface '" + args[1] + "' specified. Exiting.")
        return

    # initialize program (Model), start thread
    program = Model(args=(cmq,mvq))
    program.start()

    # ViewController: start controlling
    vc.mainloop()

if __name__=="__main__":
    main()