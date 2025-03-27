QT       += core gui
greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = NoBridgeDemo
TEMPLATE = app

SOURCES += \
    main.cpp \
    lightbutton.cpp \
    darkbutton.cpp \
    lightlabel.cpp \
    darklabel.cpp \
    thememanager.cpp \
    themeselectiondialog.cpp

HEADERS += \
    themeselectiondialog.h \
    widget.h \
    lightbutton.h \
    darkbutton.h \
    lightlabel.h \
    darklabel.h \
    thememanager.h
