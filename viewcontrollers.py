# viewcontrollers.py
# ------------------
# to define abstract methods (more useful than it sounds)
from abc import ABC, abstractmethod
# for TkViewController
from tkinter import *
from tkinter import ttk
# for a delay in the CmdViewController
import time

# abstract base class: contains the basic/common functionality
# that our viewcontrollers need to communicate with Model.
class ViewController(ABC):
    # attributes that derived classes should be agnostic of
    #   queues for async communication w/ Model (private)
    __cmd = None
    __mvq = None

    # attributes that derived classes will need (protected)
    #   views: the value of Z to be showing
    _viewZ = None
    #   flag for running: necessary for telling Model to shutdown
    _isRunning = True

    # initialize queues for async communication w/ Model
    def __init__(self, cmq, mvq):
        # controller->model queue (WRITE)
        self.__cmq = cmq
        # model->view queue (READ)
        self.__mvq = mvq

    # methods that our viewcontrollers need to implement
    #  update their interface
    @abstractmethod
    def update(self):
        pass
    #  update their drawn value of Z
    @abstractmethod
    def drawZ(self):
        pass

    # request Model to set X and Y
    def requestSet(self, setX, setY):
        self.__cmq.put({"action": "set", "dataX": setX, "dataY": setY})
    # request Model to calculate X + Y
    def requestCalc(self):
        self.__cmq.put({"action": "compute"})
    # request Model to shutdown
    def requestStop(self):
        self.__cmq.put({'action': 'die'})

    # handle Model requests
    def handleRequests(self):
        # check model->view queue
        if not self.__mvq.empty():
            request = self.__mvq.get()
            action = request["action"]
            # drawZ request: update viewZ member
            if action == "drawZ":
                self._viewZ = request["dataZ"]
                self.drawZ()

    # view controller mainloop
    def mainloop(self):
        while self._isRunning:
            # update derived class's interface, may call self._isRunning
            self.update()
            # handle requests from Model
            self.handleRequests()
        # tell Model to stop
        self.requestStop()

# ViewController using a Command-line interface
class CmdViewController(ViewController):
    def __init__(self, cmq, mvq):
        super().__init__(cmq, mvq)

    # get live command-line input to control the model object
    def update(self):
        cmds = input("> ")
        if len(cmds) == 0:
            cmds = "0"
        cmds = cmds.split()
        cmd = cmds[0]
        if cmd == "help":
            print("set X Y, where X and Y are numbers")
            print("calculate / calc")
            print("exit")
        elif cmd == "set":
            try:
                self.requestSet(float(cmds[1]), float(cmds[2]))
            except IndexError:
                pass
            except ValueError:
                pass
        elif cmd == "calculate" or cmd == "calc":
            self.requestCalc()
        elif cmd == "exit":
            self._isRunning = False
            return
        else:
            print("Input not recognized. Try `help`")
        time.sleep(0.5) # just to let model write things, a bit contrived

    def drawZ(self):
        print("(view) Z = " + str(self._viewZ))

# ViewController using a Tkinter UI
class TkViewController(ViewController):
    def __init__(self, cmq, mvq):
        super().__init__(cmq, mvq)

        # initialize Tk window, (we are the root)
        self.root = Tk()
        # set window title
        self.root.title("M-VC")
        # set size and grid
        mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        # add labels
        ttk.Label(mainframe, text="input X").grid(column=1, row=1, sticky=W)
        ttk.Label(mainframe, text="input Y").grid(column=1, row=2, sticky=W)
        ttk.Label(mainframe, text="output Z").grid(column=1, row=3, sticky=W)
        # add input entries
        self.inputX = StringVar()
        inputX_entry = ttk.Entry(mainframe, width=7, textvariable=self.inputX)
        inputX_entry.grid(column=2, row=1, sticky=(W,E))
        self.inputY = StringVar()
        inputY_entry = ttk.Entry(mainframe, width=7, textvariable=self.inputY)
        inputY_entry.grid(column=2, row=2, sticky=(W,E))
        # add output
        self.outputZ = StringVar()
        ttk.Label(mainframe, textvariable=self.outputZ).grid(column=2, row=3, sticky=(W, E))
        # add button to start calculation
        ttk.Button(mainframe, text="Calculate", command=self.calculate).grid(column=3, row=3, sticky=W)

        # configure sub-window padding
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        # put the cursor on inputX
        inputX_entry.focus()
        # bind hitting <Return> (on keyboard) to also start calculation
        self.root.bind("<Return>", self.calculate)

        # intercept 'X' to set a running flag
        def Close():
            self.root.destroy()
            self._isRunning = False
        self.root.protocol("WM_DELETE_WINDOW", Close)

    # implemented methods
    # draw the tkinter GUI, reference callbacks
    def update(self):
        # update Tk GUI
        self.root.update_idletasks()
        self.root.update()
    # draw Z
    def drawZ(self):
        self.outputZ.set(self._viewZ)

    # control model Tk Callback
    def calculate(self, *args):
        try:
            # get our inputs
            setX = float(self.inputX.get())
            setY = float(self.inputY.get())
            # tell model to set internal fields
            self.requestSet(setX, setY)
            # tell model to do work
            self.requestCalc()
        except ValueError:
            pass
