

"""
Created on Fri Mar 24 22:24:50 2023

@author: k


v1.0 ✔❌ ✅ ➕
vbuttonarray

creates a vertical array of buttons

parent - D:\dev\PROJ2\QT_OLED_TOOL\qt_oled_tool_0.py
       - D:\dev\PROJ2\QT_OLED_TOOL\qt_oled_tool_1.py
"""




#
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QPushButton
)
from .widget_helper import *

# =============================================================================
# VButtonArray - Vertical button array
# =============================================================================
class VButtonArray(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mainlayout = None
        self.buttons = []
        self.parent = parent
        self.Init_UI()

    def Init_UI(self):
        TOP = self
        self.mainlayout = createLayout(QVBoxLayout)
        attachLayOutToTopWidget(self.mainlayout, TOP)

    def addButton(self, foo, name='?', text='?', size=(5,5), origin=(10,10)):
        w = createWidget(QPushButton, name=name, text=text, size=size, origin=origin)
        w.clicked.connect(foo)
        self.buttons.append(w)
        assignWidgetToLayout(w, self.mainlayout)