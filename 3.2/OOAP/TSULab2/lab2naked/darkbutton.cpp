#include "darkbutton.h"
#include <QPushButton>

void DarkButton::render(QWidget* widget) {
    if (QPushButton* button = qobject_cast<QPushButton*>(widget)) {
        button->setStyleSheet(
            "QPushButton { background-color: #333333; color: #FFFFFF; border: 1px solid #FFFFFF; }"
            "QPushButton:hover { background-color: #555555; }"
            "QPushButton:pressed { background-color: #222222; }"
            );
    }
}
