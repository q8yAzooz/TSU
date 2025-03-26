#ifndef WIDGET_H
#define WIDGET_H

#include "theme.h"

class Widget : public QWidget
{
protected:
    Theme* theme;

public:
    Widget(Theme* t) : theme(t){}
    virtual ~Widget() = default;
    virtual void render(QWidget* widget) = 0;
    void setTheme(Theme* t) { theme = t; }
};

class Button : public Widget
{
public:
    Button(Theme* t) : Widget(t){}
    void render(QWidget* widget) override;
};

class Label : public Widget
{
public:
    Label(Theme* t) : Widget(t){}
    void render(QWidget* widget) override;
};

#endif // WIDGET_H
