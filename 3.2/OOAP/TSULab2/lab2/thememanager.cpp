#include "thememanager.h"

ThemeManager::ThemeManager() {
    addTheme("Light", new LightTheme());
    addTheme("Dark", new DarkTheme());
}

void ThemeManager::addTheme(const QString& name, Theme* theme) {
    themes.insert(name, theme);
}

Theme* ThemeManager::getTheme(const QString& name) const {
    return themes.value(name, nullptr);
}

QList<QString> ThemeManager::getThemeNames() const {
    return themes.keys();
}
