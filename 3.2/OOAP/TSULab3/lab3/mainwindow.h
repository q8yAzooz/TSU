#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QImage>
#include "ImageProcessor.h"

QT_BEGIN_NAMESPACE
class QLabel;
class QComboBox;
class QPushButton;
QT_END_NAMESPACE

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    MainWindow(QWidget* parent = nullptr);

private slots:
    void loadImage();
    void applyFilter();
    void saveImage();

private:
    void setupUI();
    void updateDisplay();

    QImage originalImage;
    QImage processedImage;
    ImageProcessor processor;

    QLabel* imageLabel;
    QComboBox* filterComboBox;
    QPushButton* loadButton;
    QPushButton* applyButton;
    QPushButton* saveButton;
};

#endif // MAINWINDOW_H
