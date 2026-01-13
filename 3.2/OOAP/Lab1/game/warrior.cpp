#include "warrior.h"

Warrior::Warrior(QObject *parent) : Character(parent) {
    health = 150;  // Warriors have more health
    damage = 20;   // Warriors deal more damage
    type = "Warrior";
}

QString Warrior::getType() const {
    return type;
}

int Warrior::getHealth() const {
    return health;
}

int Warrior::getDamage() const {
    return damage;
}

void Warrior::attack() {
    // In a real game, this would implement the warrior's attack logic
    emit attacked(damage);
} 