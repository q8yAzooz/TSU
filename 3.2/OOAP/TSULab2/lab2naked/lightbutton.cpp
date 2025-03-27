#include "lightbutton.h"
#include <QPushButton>

void LightButton::render(QWidget* widget) {
    if (QPushButton* button = qobject_cast<QPushButton*>(widget)) {
        button->setStyleSheet(
            "QPushButton { background-color: #FFFFFF; color: #000000; border: 1px solid #000000; }"
            "QPushButton:hover { background-color: #E0E0E0; }"
            "QPushButton:pressed { background-color: #B0B0B0; }"
            );
    }
}
