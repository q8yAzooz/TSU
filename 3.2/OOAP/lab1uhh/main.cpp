// main.cpp
#include <QApplication>
#include <QGraphicsView>
#include <QGraphicsRectItem>
#include <QTimer>
#include <QPushButton>
#include <QMap>

// Базовый класс предмета
class Item : public QGraphicsRectItem {
public:
    enum Type { Sword, Apple, FlameSword, None };

    Item(QColor color, Type type, QString name)
        : type(type), name(name) {
        setBrush(color);
        setRect(0, 0, 40, 40);

        // Добавляем текстовую метку
        text = new QGraphicsTextItem(name, this);
        text->setPos(5, 15);
    }

    Type type;
    QString name;
    QGraphicsTextItem* text;
};

// Фабрика предметов
class ItemFactory {
public:
    virtual Item* createItem() = 0;
};

class SwordFactory : public ItemFactory {
public:
    Item* createItem() override {
        return new Item(Qt::gray, Item::Sword, "Sword");
    }
};

class AppleFactory : public ItemFactory {
public:
    Item* createItem() override {
        return new Item(Qt::green, Item::Apple, "Apple");
    }
};

// Инвентарь с физикой
class Backpack : public QGraphicsScene {
    Q_OBJECT
public:
    QMap<QPair<Item::Type, Item::Type>, Item::Type> recipes = {
        {{Item::Sword, Item::Apple}, Item::FlameSword}
    };

    Backpack() {
        setSceneRect(0, 0, 400, 600);

        // Таймер для физики
        QTimer* timer = new QTimer(this);
        connect(timer, &QTimer::timeout, this, &Backpack::updatePhysics);
        timer->start(16);
    }

    void addItem(Item* item) {
        QGraphicsScene::addItem(item);
        items.append(item);
        item->setPos(qrand() % 360, 0);
    }

private slots:
    void updatePhysics() {
        // Гравитация и коллизии
        for(auto item : items) {
            item->moveBy(0, 2);

            // Проверка коллизий с другими предметами
            for(auto other : items) {
                if(item != other && item->collidesWithItem(other)) {
                    checkCrafting(item, other);
                }
            }
        }
    }

private:
    void checkCrafting(Item* a, Item* b) {
        auto combo1 = qMakePair(a->type, b->type);
        auto combo2 = qMakePair(b->type, a->type);

        if(recipes.contains(combo1)) {
            craftItem(combo1.first, combo1.second);
        } else if(recipes.contains(combo2)) {
            craftItem(combo2.first, combo2.second);
        }
    }

    void craftItem(Item::Type a, Item::Type b) {
        // Удаляем исходные предметы
        // ... (реализация удаления)

        // Создаем новый предмет
        Item* newItem = new Item(Qt::red, Item::FlameSword, "Flame Sword");
        addItem(newItem);
    }

    QList<Item*> items;
};

// Боевая сцена
class BattleScene : public QGraphicsScene {
public:
    BattleScene() {
        addText("Battle Started!")->setPos(100, 100);
        QPushButton* endTurnBtn = new QPushButton("End Turn");
        connect(endTurnBtn, &QPushButton::clicked, [this]{
            enemyAttack();
        });
        addWidget(endTurnBtn)->setPos(150, 200);
    }

    void enemyAttack() {
        addText("Enemy attacks for 5 damage!", QFont("Arial", 14))->setPos(100, 300);
    }
};

int main(int argc, char *argv[]) {
    QApplication a(argc, argv);

    // Создаем главное окно
    QWidget window;
    QHBoxLayout* layout = new QHBoxLayout(&window);

    // Инвентарь
    Backpack* backpack = new Backpack();
    QGraphicsView* backpackView = new QGraphicsView(backpack);
    layout->addWidget(backpackView);

    // Кнопки для добавления предметов
    QWidget* controls = new QWidget();
    QVBoxLayout* btnLayout = new QVBoxLayout(controls);

    SwordFactory swordFactory;
    QPushButton* addSwordBtn = new QPushButton("Add Sword");
    connect(addSwordBtn, &QPushButton::clicked, [&]{
        backpack->addItem(swordFactory.createItem());
    });

    AppleFactory appleFactory;
    QPushButton* addAppleBtn = new QPushButton("Add Apple");
    connect(addAppleBtn, &QPushButton::clicked, [&]{
        backpack->addItem(appleFactory.createItem());
    });

    btnLayout->addWidget(addSwordBtn);
    btnLayout->addWidget(addAppleBtn);
    layout->addWidget(controls);

    // Переход к бою
    BattleScene* battleScene = new BattleScene();
    QGraphicsView* battleView = new QGraphicsView(battleScene);
    battleView->hide();

    QPushButton* startBattleBtn = new QPushButton("Start Battle");
    connect(startBattleBtn, &QPushButton::clicked, [=]{
        backpackView->hide();
        battleView->show();
    });
    btnLayout->addWidget(startBattleBtn);

    window.resize(800, 600);
    window.show();

    return a.exec();
}

#include "main.moc"
