#include "themeselectiondialog.h"

ThemeSelectionDialog::ThemeSelectionDialog(QWidget* parent) : QDialog(parent) {
    setWindowTitle("Pick your theme");

    themeComboBox = new QComboBox();
    themeComboBox->addItems({"Light", "Dark"}); // Доступные темы

    okButton = new QPushButton("ОК");
    connect(okButton, &QPushButton::clicked, this, &QDialog::accept);

    QVBoxLayout* layout = new QVBoxLayout();
    layout->addWidget(themeComboBox);
    layout->addWidget(okButton);
    setLayout(layout);
}

QString ThemeSelectionDialog::getSelectedTheme() const {
    return themeComboBox->currentText();
}
