import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
class KeyboardWidget(QWidget):
    def __init__(self, info,parent=None):
        super(KeyboardWidget, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(1000, 600)
        self.info=info
        self.current_text = ""
        self.setStyleSheet("QWidget{\n"
"    background-color: #313a46;\n"
"}\n"
"")
        self.signalMapper = QSignalMapper(self)
        self.signalMapper.mapped[int].connect(self.buttonClicked)
        self.initUI()

    def do_caps(self):
        self.name=self.names_cap
        self.buttonAdd(3)
        self.caps_button.setStyleSheet("QPushButton{\n"
        "    background: rgb(255, 255, 255);\n"
        "\n"
        "}")
        self.caps_button.clicked.disconnect()
        self.caps_button.clicked.connect(self.do_small)
    
    def do_small(self):
        self.name=self.names
        self.buttonAdd(3)
        self.caps_button.setStyleSheet("QPushButton{\n"
        "    background: rgb(162, 168, 168);\n"
        "\n"
        "}")
        self.caps_button.clicked.disconnect()
        self.caps_button.clicked.connect(self.do_caps)
    def do_a123(self):
        self.name=self.names_a123
        self.buttonAdd(1)
        print("1")

    def initUI(self):
        self.layout = QGridLayout(self)
        
        # p = self.palette()
        # p.setColor(self.backgroundRole(),Qt.white)
        # self.setPalette(p)
        self.label=QLabel()
        self.label.setFixedHeight(60)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setStyleSheet("QLabel{\n"
"    background: rgb(255, 255, 255);\n"
"}\n"
"")
        self.label.setText(self.info)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.layout.addWidget(self.label, 0, 0, 1, 3)

        self.textEdit = QLineEdit()
        self.textEdit.setFixedHeight(60)
        self.textEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.textEdit.setFont(font)
        self.textEdit.setStyleSheet("QLineEdit{\n"
"    background: rgb(255, 255, 255);\n"
"\n"
"}")
        self.textEdit.setObjectName("textEdit")
        self.layout.addWidget(self.textEdit, 0, 3, 1, 7)

        self.names_a123= ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                 ]
        self.names_cap = ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P',
                 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K',
                 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'L'] 
        self.names = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
                 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 
                 'z', 'x', 'c', 'v', 'b', 'n', 'm', 'l']

        self.name=self.names
        self.buttonAdd(3)
        
        # Cap button
        self.caps_button = QPushButton('Caps')
        self.caps_button.setFixedHeight(70)
        self.caps_button.setFont(QFont('Arial', 16))
        self.caps_button.setStyleSheet("QPushButton{\n"
"    background: rgb(162, 168, 168);\n"
"\n"
"}")
        self.caps_button.KEY_CHAR = Qt.Key_Up
        self.layout.addWidget(self.caps_button, 2, 0, 1, 2)
        self.caps_button.clicked.connect(self.signalMapper.map)
        self.signalMapper.setMapping(self.caps_button, self.caps_button.KEY_CHAR)
        self.caps_button.clicked.connect(self.do_caps)

        # ?123 button
        self.a123_button = QPushButton('123')
        self.a123_button.setFixedHeight(70)
        self.a123_button.setFont(QFont('Arial', 16))
        self.a123_button.setStyleSheet("QPushButton{\n"
"    background: rgb(162, 168, 168);\n"
"\n"
"}")
        self.a123_button.KEY_CHAR = Qt.Key_Up
        self.layout.addWidget(self.a123_button, 3, 0, 1,2)
        self.a123_button.clicked.connect(self.signalMapper.map)
        self.signalMapper.setMapping(self.a123_button, self.a123_button.KEY_CHAR)
        self.a123_button.clicked.connect(self.do_a123)

       
        

        # Back button
        self.back_button = QPushButton('Back')
        self.back_button.setFixedHeight(70)
        self.back_button.setFont(QFont('Arial', 16))
        self.back_button.setStyleSheet("QPushButton{\n"
"    background: rgb(162, 168, 168);\n"
"\n"
"}")
        self.layout.addWidget(self.back_button, 5, 0,1,1)

        # Space button
        space_button = QPushButton('Space')
        space_button.setFixedHeight(70)
        space_button.setFont(QFont('Arial', 16))
        space_button.setStyleSheet("QPushButton{\n"
"    background: rgb(162, 168, 168);\n"
"\n"
"}")
        space_button.KEY_CHAR = Qt.Key_Space
        self.layout.addWidget(space_button, 5, 3, 1, 4 )
        space_button.clicked.connect(self.signalMapper.map)
        self.signalMapper.setMapping(space_button, space_button.KEY_CHAR)


        # Del button
        del_button = QPushButton('Del')
        del_button.setFixedHeight(70)
        del_button.setFont(QFont('Arial', 16))
        del_button.setStyleSheet("QPushButton{\n"
"    background: rgb(162, 168, 168);\n"
"\n"
"}")
        del_button.KEY_CHAR = Qt.Key_Backspace
        self.layout.addWidget(del_button, 5, 7)
        del_button.clicked.connect(self.signalMapper.map)
        self.signalMapper.setMapping(del_button, del_button.KEY_CHAR)




        # Enter button
        self.enter_button = QPushButton('Enter')
        self.enter_button.setFixedHeight(70)
        self.enter_button.setFont(QFont('Arial', 16))
        self.enter_button.setStyleSheet("QPushButton{\n"
"    background: rgb(162, 168, 168);\n"
"\n"
"}")
        self.layout.addWidget(self.enter_button, 5, 8, 1, 2)
        
        # a@ button
        acong_button = QPushButton('@')
        acong_button.setFixedHeight(70)
        acong_button.setFont(QFont('Arial', 16))
        acong_button.setStyleSheet("QPushButton{\n"
"    background: rgb(162, 168, 168);\n"
"\n"
"}")
        acong_button.KEY_CHAR = Qt.Key_Home
        self.layout.addWidget(acong_button, 5, 1)
        acong_button.clicked.connect(self.signalMapper.map)
        self.signalMapper.setMapping(acong_button, acong_button.KEY_CHAR)

        # . button
        cham_button = QPushButton('.')
        cham_button.setFixedHeight(70)
        cham_button.setFont(QFont('Arial', 16))
        cham_button.setStyleSheet("QPushButton{\n"
"    background: rgb(162, 168, 168);\n"
"\n"
"}")
        cham_button.KEY_CHAR = Qt.Key_Cancel
        self.layout.addWidget(cham_button, 5, 2)
        cham_button.clicked.connect(self.signalMapper.map)
        self.signalMapper.setMapping(cham_button, cham_button.KEY_CHAR)

        self.setLayout(self.layout)

    def buttonClicked(self, char_ord):

        txt = self.textEdit.text()
        print(txt)

        if char_ord == Qt.Key_Backspace:
            txt = txt[:-1]
        elif char_ord == Qt.Key_Home:
            txt += "@"
        elif char_ord == Qt.Key_Cancel:
            txt += "."
        elif char_ord == Qt.Key_Clear:
            txt = ""
        elif char_ord == Qt.Key_Space:
            txt += ' '
        elif char_ord == Qt.Key_Up:
            pass 
        else:
            txt +=chr(char_ord)

        self.textEdit.setText(txt)
        self.current_text = txt  # Store the current text in an instance variable
    
    def get_text(self):
        return self.current_text

    def buttonAdd(self,stt):
        positions = [(i + 1, j) for i in range(stt) for j in range(10)]
        if stt==3:
            positions.pop(10)
            positions.pop(10)
            positions.pop(18)
            positions.pop(18)
        

        for position, name in zip(positions, self.name):

            if name == '':
                continue
            button = QPushButton(name)
            button.setFont(QFont('Arial', 16))
            button.setFixedHeight(70)
            button.setStyleSheet("QPushButton{\n"
"    background: rgb(162, 168, 168);\n"
"\n"    
"}")
            button.KEY_CHAR = ord(name)
            button.clicked.connect(self.signalMapper.map)
            self.signalMapper.setMapping(button, button.KEY_CHAR)
            self.layout.addWidget(button, *position)
