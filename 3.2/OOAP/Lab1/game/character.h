#ifndef CHARACTER_H
#define CHARACTER_H

#include <QString>
#include <QObject>

class Character : public QObject {
    Q_OBJECT

public:
    explicit Character(QObject *parent = nullptr);
    virtual ~Character() = default;

    // Pure virtual methods that all characters must implement
    virtual QString getType() const = 0;
    virtual int getHealth() const = 0;
    virtual int getDamage() const = 0;
    virtual void attack() = 0;

signals:
    void attacked(int damage);

protected:
    int health;
    int damage;
    QString type;
};

#endif // CHARACTER_H 