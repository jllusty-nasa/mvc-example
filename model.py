# model.py
# --------
import threading
# when running a thread, we don't use print, use logging
import logging
#  logging config when we call logging.debug()
logging.basicConfig(level=logging.DEBUG, format='(model) %(message)s')

# Model Object
# ------------
# Program's dynamic datastructure.
# It manages data, logic, and rules.
class Model(threading.Thread):
    # program data (suggested: keep as private members)
    __dataX = None
    __dataY = None
    __dataZ = None

    # initialize program thread + set queues for async communication with a ViewController
    def __init__(self,group=None,target=None,name=None,
                 args=None, kwargs=None):
        threading.Thread.__init__(self, group=group, target=target, name=name)

        # queues for asynchronous communication with controller and view
        # controller->model queue (READ)
        self.cmq = args[0]
        # model->view queue (WRITE)
        self.mvq = args[1]

    # thread main
    def run(self):
        while True:
            # wait for viewcontroller to tell us what to do through cmq
            if not self.cmq.empty():
                request = self.cmq.get()
                action = request["action"]
                if action == "set":
                    self.__dataX = request["dataX"]
                    self.__dataY = request["dataY"]
                    logging.debug("set dataX, dataY to " + str(self.__dataX) + ", " + str(self.__dataY))
                if action == "compute":
                    self.compute()
                    logging.debug("computed dataX + dataY = dataZ = " + str(self.__dataZ))
                    # computing is done, so tell view to update dataZ
                    self.mvq.put({"action": "drawZ", "dataZ": self.__dataZ})
                elif action == "die":
                    logging.debug("exiting")
                    return

    # pass data
    def setData(self, dataX, dataY):
        self.__dataX = dataX
        self.__dataY = dataY

    # get data
    def getData(self):
        return self.__dataZ

    # do something with our data
    def compute(self):
        if self.__dataX is not None and self.__dataY is not None:
            try:
                self.__dataZ = self.__dataX + self.__dataY
            except ValueError:
                pass
