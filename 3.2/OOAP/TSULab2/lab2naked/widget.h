#ifndef WIDGET_H
#define WIDGET_H

#include <QWidget>

class Widget {
public:
    virtual ~Widget() = default;
    virtual void render(QWidget* widget) = 0;
};

#endif // WIDGET_H
