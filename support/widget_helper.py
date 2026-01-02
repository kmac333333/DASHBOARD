



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
from PyQt6.QtWidgets import (
    QGridLayout, QFrame
)


# ==============================================================================
# pyqt widget helpers for me
# ==============================================================================
def createWidget(widget, parent=None, id=None, model=None, name=None, align=None,
                 modelkey="", vectorlabels=None,  text="", title="",
                 origin=(5, 5), size=(10, 10),):
    #
    t = widget.staticMetaObject.className() # get real widget name - not wrapper crap
    # ======================= pyqt widgets
    if t == "QLabel":
        w = widget(parent)
        w.setText(text)
    #
    if t == "QPushButton":
        w = widget(parent)
        w.setText(text)
    #
    if t == "QLineEdit":
        w = widget(parent)
        w.setText(text)
    #
    if t == "QSpinBox":
        w = widget(parent)
    #
    if t == "QComboBox":
        w = widget(parent)
    #
    if t == "QFrame":
        w = widget(parent)
    # ======================= user widgets
    if t == "FileInputWidget":
        w = widget(parent, text=text)
    if t == "LocationArray":
        w = widget(parent)
    if t == "LabeledValue":
        w = widget(parent, text=text)
    #
    if t == "Vec4":
        w = widget(parent, model=model)
        w.setText(text)
    if t == "myCanvas":
        w = widget(parent, model=model)
    if t == "VButtonArray":
        w = widget(parent)
    if t == "Vec4ControlWidget":
        w = widget(parent, model=model,  modelkey=modelkey, vectorlabels=vectorlabels)
    #
    if t == "Vec4":
        w = widget(parent, model=model)
        w.setText(text)
    #
    if t == "Vec1":
        w = widget(parent)
        w.setText(text)
    #
    if t == "GraphArea":
        w = widget(parent)
        w.setModel(model)
        w.setTitle(title)
    #
    if t == "Pane":
        w = widget(parent)
        
    if t == "MQTTFrame":
        w = widget(parent)
    #
    if align is not None:
        w.setAlignment(align)
    #
    if size is not None:
        w.setFixedSize(size[0], size[1])
    #
    if origin is not None:
        w.move(origin[0], origin[1])
    #
    w.setObjectName(name)
    return w
#
def createLayout(layout, parent=None, name=None, align=None):
    l = layout(parent)
    l.setObjectName(name)
    if align is not None:
        l.setAlignment(align)
    return l
#
def attachLayOutToTopWidget(layout, topwidget):
    topwidget.setLayout(layout)
#
def attachNestedLayout(childlayout, parentlayout):
    parentlayout.addLayout(childlayout)
#
def assignWidgetToLayout(widget, layout, row=0, col=0):
    if (type(layout)) is QGridLayout:
        layout.addWidget(widget, row, col)
    else:
        layout.addWidget(widget)