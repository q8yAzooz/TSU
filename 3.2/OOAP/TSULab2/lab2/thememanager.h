#ifndef THEMEMANAGER_H
#define THEMEMANAGER_H

#include "theme.h"
#include <QList>
#include <QMap>

class ThemeManager {
public:
    ThemeManager();
    void addTheme(const QString& name, Theme* theme);
    Theme* getTheme(const QString& name) const;
    QList<QString> getThemeNames() const;

private:
    QMap<QString, Theme*> themes;
};

#endif // THEMEMANAGER_H
