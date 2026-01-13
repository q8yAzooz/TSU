#ifndef CHARACTERFACTORY_H
#define CHARACTERFACTORY_H

#include "character.h"
#include <QString>

class CharacterFactory {
public:
    static Character* createCharacter(const QString& type, QObject* parent = nullptr);
};

#endif // CHARACTERFACTORY_H 