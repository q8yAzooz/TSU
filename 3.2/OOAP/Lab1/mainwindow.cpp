#include "mainwindow.h"
#include "./ui_mainwindow.h"
#include <QMessageBox>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
    , currentCharacter(nullptr)
{
    ui->setupUi(this);
    
    // Create central widget and layout
    centralWidget = new QWidget(this);
    setCentralWidget(centralWidget);
    layout = new QVBoxLayout(centralWidget);
    
    // Create status label
    statusLabel = new QLabel("No character created", this);
    layout->addWidget(statusLabel);
    
    // Create buttons
    QPushButton *createWarriorBtn = new QPushButton("Create Warrior", this);
    layout->addWidget(createWarriorBtn);
    
    QPushButton *attackBtn = new QPushButton("Attack", this);
    layout->addWidget(attackBtn);
    
    // Connect signals and slots
    connect(createWarriorBtn, &QPushButton::clicked, this, &MainWindow::createWarrior);
    connect(attackBtn, &QPushButton::clicked, [this]() {
        if (currentCharacter) {
            currentCharacter->attack();
        }
    });
}

MainWindow::~MainWindow()
{
    delete ui;
    delete currentCharacter;
}

void MainWindow::createWarrior() {
    if (currentCharacter) {
        delete currentCharacter;
    }
    
    currentCharacter = CharacterFactory::createCharacter("Warrior", this);
    if (currentCharacter) {
        connect(currentCharacter, &Character::attacked, this, &MainWindow::onCharacterAttacked);
        statusLabel->setText(QString("Created %1 (Health: %2, Damage: %3)")
            .arg(currentCharacter->getType())
            .arg(currentCharacter->getHealth())
            .arg(currentCharacter->getDamage()));
    }
}

void MainWindow::onCharacterAttacked(int damage) {
    QMessageBox::information(this, "Attack", 
        QString("Character attacked for %1 damage!").arg(damage));
}
