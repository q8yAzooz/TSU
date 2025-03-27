#ifndef THEMEMANAGER_H
#define THEMEMANAGER_H

#include <QMap>
#include <QString>

class Widget;

class ThemeManager {
public:
    ThemeManager();
    ~ThemeManager();
    Widget* getButton(const QString& themeName);
    Widget* getLabel(const QString& themeName);

private:
    QMap<QString, Widget*> buttons;
    QMap<QString, Widget*> labels;
};

#endif // THEMEMANAGER_H
