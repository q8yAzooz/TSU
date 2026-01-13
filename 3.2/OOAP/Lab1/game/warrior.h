#ifndef WARRIOR_H
#define WARRIOR_H

#include "character.h"

class Warrior : public Character {
    Q_OBJECT

public:
    explicit Warrior(QObject *parent = nullptr);
    QString getType() const override;
    int getHealth() const override;
    int getDamage() const override;
    void attack() override;
};

#endif // WARRIOR_H 