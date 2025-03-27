#include "theme.h"

void LightTheme::applyStyle(QWidget* widget) {
    if (qobject_cast<QPushButton*>(widget)) {
        widget->setStyleSheet(
            "QPushButton { background-color: #FFFFFF; color: #000000; border: 1px solid #000000; }"
            "QPushButton:hover { background-color: #E0E0E0; }"
            "QPushButton:pressed { background-color: #B0B0B0; }"
            );
    } else if (qobject_cast<QLineEdit*>(widget)) {
        widget->setStyleSheet("background-color: #FFFFFF; color: #000000; border: 1px solid #000000;");
    } else if (qobject_cast<QCheckBox*>(widget)) {
        widget->setStyleSheet("color: #000000;");
    } else if (qobject_cast<QComboBox*>(widget)) {
        widget->setStyleSheet(
            "QComboBox { background-color: #FFFFFF; color: #000000; border: 1px solid #000000; }"
            "QComboBox QAbstractItemView { background-color: #FFFFFF; color: #000000; }"
            );
    } else if (qobject_cast<QSlider*>(widget)) {
        widget->setStyleSheet(
            "QSlider::groove:horizontal { background-color: #E0E0E0; height: 8px; }"
            "QSlider::handle:horizontal { background-color: #000000; width: 16px; }"
            );
    } else if (qobject_cast<QTextEdit*>(widget)) {
        widget->setStyleSheet("background-color: #FFFFFF; color: #000000; border: 1px solid #000000;");
    } else {
        widget->setStyleSheet("background-color: #FFFFFF; color: #000000; border: 1px solid #000000;");
    }
}

void DarkTheme::applyStyle(QWidget* widget) {
    if (qobject_cast<QPushButton*>(widget)) {
        widget->setStyleSheet(
            "QPushButton { background-color: #333333; color: #FFFFFF; border: 1px solid #FFFFFF; }"
            "QPushButton:hover { background-color: #555555; }"
            "QPushButton:pressed { background-color: #222222; }"
            );
    } else if (qobject_cast<QLineEdit*>(widget)) {
        widget->setStyleSheet("background-color: #333333; color: #FFFFFF; border: 1px solid #FFFFFF;");
    } else if (qobject_cast<QCheckBox*>(widget)) {
        widget->setStyleSheet("color: #FFFFFF;");
    } else if (qobject_cast<QComboBox*>(widget)) {
        widget->setStyleSheet(
            "QComboBox { background-color: #333333; color: #FFFFFF; border: 1px solid #FFFFFF; }"
            "QComboBox QAbstractItemView { background-color: #333333; color: #FFFFFF; }"
            );
    } else if (qobject_cast<QSlider*>(widget)) {
        widget->setStyleSheet(
            "QSlider::groove:horizontal { background-color: #555555; height: 8px; }"
            "QSlider::handle:horizontal { background-color: #FFFFFF; width: 16px; }"
            );
    } else if (qobject_cast<QTextEdit*>(widget)) {
        widget->setStyleSheet("background-color: #333333; color: #FFFFFF; border: 1px solid #FFFFFF;");
    } else {
        widget->setStyleSheet("background-color: #333333; color: #FFFFFF; border: 1px solid #FFFFFF;");
    }
}

CustomTheme::CustomTheme(const QString& bgColor, const QString& textColor, const QString& borderColor)
    : bgColor(bgColor), textColor(textColor), borderColor(borderColor) {}

void CustomTheme::applyStyle(QWidget* widget) {
    if (qobject_cast<QPushButton*>(widget)) {
        widget->setStyleSheet(
            "QPushButton { background-color: " + bgColor + "; color: " + textColor + "; border: 1px solid " + borderColor + "; }"
                                                                                                                            "QPushButton:hover { background-color: " + bgColor + "; }"
                        "QPushButton:pressed { background-color: " + bgColor + "; }"
            );
    } else if (qobject_cast<QLineEdit*>(widget)) {
        widget->setStyleSheet("background-color: " + bgColor + "; color: " + textColor + "; border: 1px solid " + borderColor + ";");
    } else if (qobject_cast<QCheckBox*>(widget)) {
        widget->setStyleSheet("color: " + textColor + ";");
    } else if (qobject_cast<QComboBox*>(widget)) {
        widget->setStyleSheet(
            "QComboBox { background-color: " + bgColor + "; color: " + textColor + "; border: 1px solid " + borderColor + "; }"
                                                                                                                          "QComboBox QAbstractItemView { background-color: " + bgColor + "; color: " + textColor + "; }"
            );
    } else if (qobject_cast<QSlider*>(widget)) {
        widget->setStyleSheet(
            "QSlider::groove:horizontal { background-color: " + bgColor + "; height: 8px; }"
                                                                          "QSlider::handle:horizontal { background-color: " + textColor + "; width: 16px; }"
            );
    } else if (qobject_cast<QTextEdit*>(widget)) {
        widget->setStyleSheet("background-color: " + bgColor + "; color: " + textColor + "; border: 1px solid " + borderColor + ";");
    } else {
        widget->setStyleSheet("background-color: " + bgColor + "; color: " + textColor + "; border: 1px solid " + borderColor + ";");
    }
}
