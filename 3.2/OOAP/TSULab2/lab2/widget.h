#ifndef WIDGET_H
#define WIDGET_H

#include "theme.h"
#include <QWidget>

class Widget {
public:
    Widget(Theme* theme) : theme(theme) {}
    virtual void render(QWidget* widget) = 0;
    void setTheme(Theme* newTheme) { theme = newTheme; }

protected:
    Theme* theme;
};

class Button : public Widget {
public:
    Button(Theme* theme) : Widget(theme) {}
    void render(QWidget* widget) override { theme->applyStyle(widget); }
};

class Label : public Widget {
public:
    Label(Theme* theme) : Widget(theme) {}
    void render(QWidget* widget) override { theme->applyStyle(widget); }
};

class LineEdit : public Widget {
public:
    LineEdit(Theme* theme) : Widget(theme) {}
    void render(QWidget* widget) override { theme->applyStyle(widget); }
};

class CheckBox : public Widget {
public:
    CheckBox(Theme* theme) : Widget(theme) {}
    void render(QWidget* widget) override { theme->applyStyle(widget); }
};

class ComboBox : public Widget {
public:
    ComboBox(Theme* theme) : Widget(theme) {}
    void render(QWidget* widget) override { theme->applyStyle(widget); }
};

class Slider : public Widget {
public:
    Slider(Theme* theme) : Widget(theme) {}
    void render(QWidget* widget) override { theme->applyStyle(widget); }
};

class TextEdit : public Widget {
public:
    TextEdit(Theme* theme) : Widget(theme) {}
    void render(QWidget* widget) override { theme->applyStyle(widget); }
};

#endif // WIDGET_H
