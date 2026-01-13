#include "characterfactory.h"
#include "warrior.h"

Character* CharacterFactory::createCharacter(const QString& type, QObject* parent) {
    if (type == "Warrior") {
        return new Warrior(parent);
    }
    // Add more character types here as needed
    return nullptr;
} 