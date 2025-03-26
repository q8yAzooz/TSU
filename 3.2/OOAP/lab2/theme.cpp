#include "theme.h"

void LightTheme::applyStyle(QWidget* widget) {
    if (qobject_cast<QPushButton*>(widget)) {
        widget->setStyleSheet(
            "QPushButton {"
            "   background-color: #FFFFFF;"
            "   color: #000000;"
            "   border: 1px solid #000000;"
            "}"
            "QPushButton:hover {"
            "   background-color: #E0E0E0;"
            "}"
            "QPushButton:pressed {"
            "   background-color: #B0B0B0;"
            "}"
            );
    } else {
        widget->setStyleSheet(
            "background-color: #FFFFFF;"
            "color: #000000;"
            "border: 1px solid #000000;"
            );
    }
}

void DarkTheme::applyStyle(QWidget* widget) {
    if (qobject_cast<QPushButton*>(widget)) {
        widget->setStyleSheet(
            "QPushButton {"
            "   background-color: #333333;"
            "   color: #FFFFFF;"
            "   border: 1px solid #FFFFFF;"
            "}"
            "QPushButton:hover {"
            "   background-color: #555555;"
            "}"
            "QPushButton:pressed {"
            "   background-color: #222222;"
            "}"
            );
    } else {
        widget->setStyleSheet(
            "background-color: #333333;"
            "color: #FFFFFF;"
            "border: 1px solid #FFFFFF;"
            );
    }
}
