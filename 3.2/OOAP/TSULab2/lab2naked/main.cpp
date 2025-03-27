#include <QApplication>
#include "themeselectiondialog.h"
#include <QPushButton>
#include <QLabel>
#include <QVBoxLayout>
#include <QMessageBox>

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    // Показываем диалоговое окно для выбора темы
    ThemeSelectionDialog dialog;
    if (dialog.exec() != QDialog::Accepted) {
        return 0; // Если пользователь закрыл диалог, выходим
    }

    QString selectedTheme = dialog.getSelectedTheme();

    // Создаём основное окно
    QWidget window;
    window.setWindowTitle("No bridg:(");
    QVBoxLayout* layout = new QVBoxLayout(&window);

    // Создаём виджеты
    QPushButton* button = new QPushButton("Push me!");
    QLabel* label = new QLabel("This is a label");

    // Применяем стили в зависимости от выбранной темы
    if (selectedTheme == "Light") {
        button->setStyleSheet("background-color: white; color: black;");
        label->setStyleSheet("background-color: white; color: black;");
    } else if (selectedTheme == "Dark") {
        button->setStyleSheet("background-color: gray; color: white;");
        label->setStyleSheet("background-color: gray; color: white;");
    }

    // Добавляем обработчик нажатия кнопки
    QObject::connect(button, &QPushButton::clicked, [&]() {
        QMessageBox::information(&window, "Button is pressed", "The button works!");
    });

    // Добавляем виджеты в layout
    layout->addWidget(label);
    layout->addWidget(button);
    window.setLayout(layout);
    window.show();

    return app.exec();
}
