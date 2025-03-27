#include "lightlabel.h"
#include <QLabel>

void LightLabel::render(QWidget* widget) {
    if (QLabel* label = qobject_cast<QLabel*>(widget)) {
        label->setStyleSheet(
            "QLabel { background-color: #FFFFFF; color: #000000; border: 1px solid #000000; }"
            );
    }
}
