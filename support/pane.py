

"""
Created on Fri Mar 24 22:24:50 2023

@author: k


v1.0 ✔❌ ✅ ➕
vbuttonarray

creates a a panes for the oled app

parent - D:\dev\PROJ2\QT_OLED_TOOL\qt_oled_tool_0.py
       - D:\dev\PROJ2\QT_OLED_TOOL\qt_oled_tool_1.py
"""




#
from PyQt5.QtWidgets import (
    QFrame
)



# =============================================================================
# Panes
# =============================================================================
class Pane(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widgets = []
        self.layout = None
        self.vec4A = None
        self.parent = parent
        self.setFrameShape(QFrame.StyledPanel)
        self.Init_UI()
    #
    def Init_UI(self):
        # container
        self.setObjectName(f"{self.metaObject().className()}")
        # layout
        # self.layout = createLayout(QHBoxLayout)

        # attachLayOutToTopWidget(self.layout, self)
    #
    def addWidgetToPane(self, w, x, y):
        # assignWidgetToLayout(w, self.layout)
        self.widgets.append(w)
        w.setParent(self)
        w.move(x, y)