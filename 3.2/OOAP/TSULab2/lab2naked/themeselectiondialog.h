#ifndef THEMESELECTIONDIALOG_H
#define THEMESELECTIONDIALOG_H

#include <QDialog>
#include <QComboBox>
#include <QPushButton>
#include <QVBoxLayout>

class ThemeSelectionDialog : public QDialog {
    Q_OBJECT
public:
    ThemeSelectionDialog(QWidget* parent = nullptr);
    QString getSelectedTheme() const;

private:
    QComboBox* themeComboBox;
    QPushButton* okButton;
};

#endif // THEMESELECTIONDIALOG_H
