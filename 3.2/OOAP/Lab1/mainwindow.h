#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QPushButton>
#include <QLabel>
#include <QVBoxLayout>
#include "game/character.h"
#include "game/characterfactory.h"

QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void createWarrior();
    void onCharacterAttacked(int damage);

private:
    Ui::MainWindow *ui;
    QWidget *centralWidget;
    QVBoxLayout *layout;
    QLabel *statusLabel;
    Character *currentCharacter;
};

#endif // MAINWINDOW_H
