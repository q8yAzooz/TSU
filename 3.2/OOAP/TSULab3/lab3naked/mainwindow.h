#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QImage>

class QLabel;
class QComboBox;
class QPushButton;

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);

private slots:
    void loadImage();
    void applyFilter();
    void saveImage();

private:
    void applyGrayscale(QImage &image);
    void applySepia(QImage &image);
    void updateDisplay();

    QImage originalImage;
    QImage processedImage;

    // UI элементы
    QLabel *imageLabel;
    QComboBox *filterComboBox;
    QPushButton *loadButton;
    QPushButton *applyButton;
    QPushButton *saveButton;
};

#endif // MAINWINDOW_H
