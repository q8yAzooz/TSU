#include "widget.h"
#include "theme.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    // Создаём окно
    QWidget window;
    window.setWindowTitle("Lab2");
    QVBoxLayout* layout = new QVBoxLayout(&window);

    // Создаём темы
    LightTheme lightTheme;
    DarkTheme darkTheme;

    // Создаём виджеты с начальной темой (светлая)
    Button button(&lightTheme);
    Label label(&lightTheme);

    // Создаём Qt-виджеты
    QPushButton qtButton("Click Me");
    QLabel qtLabel("This is a Label");

    // Применяем начальную тему
    button.render(&qtButton);
    label.render(&qtLabel);

    // Подключаем действие для кнопки, чтобы убедиться, что она кликабельна
    QObject::connect(&qtButton, &QPushButton::clicked, [&]() {
        QMessageBox::information(&window, "Button Clicked", "The button works!");
    });

    // Добавляем виджеты в layout
    layout->addWidget(&qtLabel);
    layout->addWidget(&qtButton);

    // Кнопка для смены темы
    QPushButton switchButton("Switch Theme");
    layout->addWidget(&switchButton);

    // Логика переключения темы
    static bool isLight = true;
    QObject::connect(&switchButton, &QPushButton::clicked, [&]() {
        if (isLight) {
            button.setTheme(&darkTheme);
            label.setTheme(&darkTheme);
        } else {
            button.setTheme(&lightTheme);
            label.setTheme(&lightTheme);
        }
        button.render(&qtButton);
        label.render(&qtLabel);
        isLight = !isLight;
    });

    // Показываем окно
    window.setLayout(layout);
    window.show();

    return app.exec();
}
