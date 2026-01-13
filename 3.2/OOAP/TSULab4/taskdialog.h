#ifndef TASKDIALOG_H
#define TASKDIALOG_H
// taskdialog.h
#include <QDialog>
#include <QLineEdit>
#include <QTextEdit>
#include <QDialogButtonBox>
#include <QFormLayout>

class TaskDialog : public QDialog {
    Q_OBJECT

public:
    explicit TaskDialog(QWidget* parent = nullptr)
        : QDialog(parent), titleEdit(new QLineEdit), descriptionEdit(new QTextEdit) {
        QFormLayout* layout = new QFormLayout(this);
        layout->addRow("Title:", titleEdit);
        layout->addRow("Description:", descriptionEdit);

        QDialogButtonBox* buttonBox = new QDialogButtonBox(
            QDialogButtonBox::Ok | QDialogButtonBox::Cancel,
            this
            );

        layout->addRow(buttonBox);

        connect(buttonBox, &QDialogButtonBox::accepted, this, &QDialog::accept);
        connect(buttonBox, &QDialogButtonBox::rejected, this, &QDialog::reject);
    }

    QString title() const { return titleEdit->text(); }
    QString description() const { return descriptionEdit->toPlainText(); }

    void setTitle(const QString& title) { titleEdit->setText(title); }
    void setDescription(const QString& desc) { descriptionEdit->setPlainText(desc); }

private:
    QLineEdit* titleEdit;
    QTextEdit* descriptionEdit;
};
#endif // TASKDIALOG_H
