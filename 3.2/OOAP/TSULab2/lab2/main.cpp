#include "widget.h"
#include "theme.h"
#include "thememanager.h"
#include "newthemedialog.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    QWidget window;
    window.setWindowTitle("Bridg:)");
    QVBoxLayout* layout = new QVBoxLayout(&window);

    // Создаём менеджер тем
    ThemeManager themeManager;

    // Создаём виджеты с начальной темой (Light)
    Button button(themeManager.getTheme("Light"));
    Label label(themeManager.getTheme("Light"));
    LineEdit lineEdit(themeManager.getTheme("Light"));
    CheckBox checkBox(themeManager.getTheme("Light"));
    ComboBox comboBox(themeManager.getTheme("Light"));
    Slider slider(themeManager.getTheme("Light"));
    TextEdit textEdit(themeManager.getTheme("Light"));

    // Qt виджеты
    QPushButton qtButton("Click Me");
    QLabel qtLabel("This is a Label");
    QLineEdit qtLineEdit;
    QCheckBox qtCheckBox("Check me");
    QComboBox qtComboBox;
    qtComboBox.addItems({"Option 1", "Option 2", "Option 3"});
    QSlider qtSlider(Qt::Horizontal);
    qtSlider.setRange(0, 100);
    qtSlider.setValue(50);
    QTextEdit qtTextEdit;
    qtTextEdit.setPlaceholderText("Enter text here...");

    // Применяем начальную тему
    button.render(&qtButton);
    label.render(&qtLabel);
    lineEdit.render(&qtLineEdit);
    checkBox.render(&qtCheckBox);
    comboBox.render(&qtComboBox);
    slider.render(&qtSlider);
    textEdit.render(&qtTextEdit);

    // Подключаем действие для кнопки
    QObject::connect(&qtButton, &QPushButton::clicked, [&]() {
        QMessageBox::information(&window, "Button Clicked", "The button works!");
    });

    // Создаём виджет для примера темы
    QWidget* exampleWidget = new QWidget();
    QVBoxLayout* exampleLayout = new QVBoxLayout(exampleWidget);
    exampleLayout->addWidget(&qtLabel);
    exampleLayout->addWidget(&qtButton);
    exampleLayout->addWidget(&qtLineEdit);
    exampleLayout->addWidget(&qtCheckBox);
    exampleLayout->addWidget(&qtComboBox);
    exampleLayout->addWidget(&qtSlider);
    exampleLayout->addWidget(&qtTextEdit);
    exampleLayout->addStretch();  // Пружина

    // Кнопка для создания новой темы
    QPushButton* newThemeButton = new QPushButton("Create New Theme");

    // Область для каталога тем
    QScrollArea* scrollArea = new QScrollArea();
    QWidget* themeCatalog = new QWidget();
    QVBoxLayout* catalogLayout = new QVBoxLayout(themeCatalog);

    // Функция для обновления каталога
    auto updateCatalog = [&](ThemeManager& manager, Button& button, Label& label, LineEdit& lineEdit,
                             CheckBox& checkBox, ComboBox& comboBox, Slider& slider, TextEdit& textEdit) {
        while (QLayoutItem* item = catalogLayout->takeAt(0)) {
            delete item->widget();
            delete item;
        }
        for (const QString& themeName : manager.getThemeNames()) {
            QPushButton* themeButton = new QPushButton(themeName);
            catalogLayout->addWidget(themeButton);
            QObject::connect(themeButton, &QPushButton::clicked, [&, themeName]() {
                Theme* selectedTheme = manager.getTheme(themeName);
                if (selectedTheme) {
                    button.setTheme(selectedTheme);
                    label.setTheme(selectedTheme);
                    lineEdit.setTheme(selectedTheme);
                    checkBox.setTheme(selectedTheme);
                    comboBox.setTheme(selectedTheme);
                    slider.setTheme(selectedTheme);
                    textEdit.setTheme(selectedTheme);
                    button.render(&qtButton);
                    label.render(&qtLabel);
                    lineEdit.render(&qtLineEdit);
                    checkBox.render(&qtCheckBox);
                    comboBox.render(&qtComboBox);
                    slider.render(&qtSlider);
                    textEdit.render(&qtTextEdit);
                }
            });
        }
        catalogLayout->addStretch();
    };

    // Инициализируем каталог
    updateCatalog(themeManager, button, label, lineEdit, checkBox, comboBox, slider, textEdit);
    scrollArea->setWidget(themeCatalog);
    scrollArea->setWidgetResizable(true);

    // Собираем основной layout
    layout->addWidget(exampleWidget);
    layout->addWidget(newThemeButton);
    layout->addWidget(scrollArea);
    layout->setStretch(0, 1);
    layout->setStretch(1, 0);
    layout->setStretch(2, 0);

    // Логика создания новой темы
    QObject::connect(newThemeButton, &QPushButton::clicked, [&]() {
        NewThemeDialog dialog(&window);
        if (dialog.exec() == QDialog::Accepted) {
            QString name = dialog.getThemeName();
            QString bgColor = dialog.getBackgroundColor();
            QString textColor = dialog.getTextColor();
            QString borderColor = dialog.getBorderColor();
            if (!name.isEmpty() && !bgColor.isEmpty() && !textColor.isEmpty() && !borderColor.isEmpty()) {
                Theme* newTheme = new CustomTheme(bgColor, textColor, borderColor);
                themeManager.addTheme(name, newTheme);
                updateCatalog(themeManager, button, label, lineEdit, checkBox, comboBox, slider, textEdit);
            } else {
                QMessageBox::warning(&window, "Invalid Input", "Please fill all fields.");
            }
        }
    });

    window.setLayout(layout);
    window.show();

    return app.exec();
}
