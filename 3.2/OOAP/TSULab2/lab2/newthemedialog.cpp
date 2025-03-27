#include "newthemedialog.h"
#include <QVBoxLayout>
#include <QLabel>
#include <QPushButton>

NewThemeDialog::NewThemeDialog(QWidget* parent) : QDialog(parent) {
    setWindowTitle("Create New Theme");
    QVBoxLayout* layout = new QVBoxLayout(this);

    layout->addWidget(new QLabel("Theme Name:"));
    nameEdit = new QLineEdit();
    layout->addWidget(nameEdit);

    layout->addWidget(new QLabel("Background Color (e.g., #FFFFFF):"));
    bgColorEdit = new QLineEdit();
    layout->addWidget(bgColorEdit);

    layout->addWidget(new QLabel("Text Color (e.g., #000000):"));
    textColorEdit = new QLineEdit();
    layout->addWidget(textColorEdit);

    layout->addWidget(new QLabel("Border Color (e.g., #000000):"));
    borderColorEdit = new QLineEdit();
    layout->addWidget(borderColorEdit);

    QPushButton* okButton = new QPushButton("OK");
    QPushButton* cancelButton = new QPushButton("Cancel");
    layout->addWidget(okButton);
    layout->addWidget(cancelButton);

    connect(okButton, &QPushButton::clicked, this, &QDialog::accept);
    connect(cancelButton, &QPushButton::clicked, this, &QDialog::reject);
}

QString NewThemeDialog::getThemeName() const { return nameEdit->text(); }
QString NewThemeDialog::getBackgroundColor() const { return bgColorEdit->text(); }
QString NewThemeDialog::getTextColor() const { return textColorEdit->text(); }
QString NewThemeDialog::getBorderColor() const { return borderColorEdit->text(); }
