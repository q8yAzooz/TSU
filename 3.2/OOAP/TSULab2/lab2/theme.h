#ifndef THEME_H
#define THEME_H

#include <QWidget>
#include <QString>
#include <QApplication>
#include <QPushButton>
#include <QLabel>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QScrollArea>
#include <QMessageBox>
#include <QLineEdit>
#include <QCheckBox>
#include <QComboBox>
#include <QSlider>
#include <QTextEdit>


class Theme {
public:
    virtual ~Theme() = default;
    virtual void applyStyle(QWidget* widget) = 0;
};

class LightTheme : public Theme {
public:
    void applyStyle(QWidget* widget) override;
};

class DarkTheme : public Theme {
public:
    void applyStyle(QWidget* widget) override;
};

class CustomTheme : public Theme {
public:
    CustomTheme(const QString& bgColor, const QString& textColor, const QString& borderColor);
    void applyStyle(QWidget* widget) override;

private:
    QString bgColor;
    QString textColor;
    QString borderColor;
};

#endif // THEME_H
