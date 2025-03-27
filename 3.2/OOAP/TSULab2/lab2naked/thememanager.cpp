#include "thememanager.h"
#include "lightbutton.h"
#include "darkbutton.h"
#include "lightlabel.h"
#include "darklabel.h"

ThemeManager::ThemeManager() {
    buttons.insert("Light", new LightButton());
    buttons.insert("Dark", new DarkButton());
    labels.insert("Light", new LightLabel());
    labels.insert("Dark", new DarkLabel());
}

ThemeManager::~ThemeManager() {
    qDeleteAll(buttons);
    qDeleteAll(labels);
    buttons.clear();
    labels.clear();
}

Widget* ThemeManager::getButton(const QString& themeName) {
    return buttons.value(themeName, nullptr);
}

Widget* ThemeManager::getLabel(const QString& themeName) {
    return labels.value(themeName, nullptr);
}
