#ifndef NEWTHEMEDIALOG_H
#define NEWTHEMEDIALOG_H

#include <QDialog>
#include <QLineEdit>

class NewThemeDialog : public QDialog {
    Q_OBJECT
public:
    NewThemeDialog(QWidget* parent = nullptr);
    QString getThemeName() const;
    QString getBackgroundColor() const;
    QString getTextColor() const;
    QString getBorderColor() const;

private:
    QLineEdit* nameEdit;
    QLineEdit* bgColorEdit;
    QLineEdit* textColorEdit;
    QLineEdit* borderColorEdit;
};

#endif // NEWTHEMEDIALOG_H
