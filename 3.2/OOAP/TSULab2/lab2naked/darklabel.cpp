#include "darklabel.h"
#include <QLabel>

void DarkLabel::render(QWidget* widget) {
    if (QLabel* label = qobject_cast<QLabel*>(widget)) {
        label->setStyleSheet(
            "QLabel { background-color: #333333; color: #FFFFFF; border: 1px solid #FFFFFF; }"
            );
    }
}
