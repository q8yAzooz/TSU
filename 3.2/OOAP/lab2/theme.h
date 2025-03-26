#ifndef THEME_H
#define THEME_H

#include <QWidget>
#include <QApplication>
#include <QPushButton>
#include <QLabel>
#include <QVBoxLayout>
#include <QMessageBox>

class Theme
{
public:
    virtual ~Theme() = default;
    virtual void applyStyle(QWidget* widget) = 0;
};

class LightTheme : public Theme
{
public:
    void applyStyle(QWidget* widget) override;
};

class DarkTheme : public Theme
{
public:
    void applyStyle(QWidget* widget) override;
};

#endif
