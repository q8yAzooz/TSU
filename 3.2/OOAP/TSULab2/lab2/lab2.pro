QT       += core gui
greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = BridgePatternDemo
TEMPLATE = app

SOURCES += main.cpp \
           widget.cpp \
           theme.cpp \
           thememanager.cpp \
           newthemedialog.cpp

HEADERS += widget.h \
           theme.h \
           thememanager.h \
           newthemedialog.h
