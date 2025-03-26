#include "widget.h"

void Button::render(QWidget *widget)
{
    theme -> applyStyle(widget);
    widget -> setMinimumSize(100, 30);
}

void Label::render(QWidget *widget)
{
    theme -> applyStyle(widget);
    widget -> setMinimumSize(150, 20);
}
