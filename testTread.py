from PySide.QtCore import *
from PySide.QtGui import *
import time




class Button1Thread(QThread):


    def __init__(self):
        QThread.__init__(self)


    def run(self):
        print("Button1")
        time.sleep(3)


class Button2Thread(QThread):


    def __init__(self):
        QThread.__init__(self)


    def run(self):
        print("Button2")

        self.counter = 0
        while self.counter <=100:
            print(self.counter)
            if self.counter == 50:
                self.emit(SIGNAL('xxx(int)'),self.counter)
                time.sleep(1)

            self.counter +=1




class MainWindow(QMainWindow):



    def __init__(self):
        super(MainWindow,self).__init__()


        self.layout = QVBoxLayout()

        self.button1 = QPushButton("Button1")
        self.thread1 = Button1Thread()
        self.connect(self.thread1,SIGNAL("finished()"),self.done1)
        self.button1.pressed.connect(self.startT1)
        self.button2 = QPushButton("Button2")
        self.thread2 = Button2Thread()
        self.connect(self.thread2,SIGNAL("xxx(int)"),self.printMsg)
        self.connect(self.thread2,SIGNAL("finished()"),self.done2)
        self.button2.pressed.connect(self.startT2)


        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)



        w = QWidget()
        w.setLayout(self.layout)
        self.setCentralWidget(w)
        self.show()

    def startT1(self):

        self.thread1.start()

    def startT2(self):

        self.thread2.start()

    def done1(done):
        print("Ended 1")
       
    def done2(done):
        print("Ended 2")

    def printMsg(self,a):
        print("reached "+str(a))

app = QApplication([])
window = MainWindow()
app.exec_()
