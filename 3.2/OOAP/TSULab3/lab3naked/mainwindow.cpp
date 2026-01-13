#include "MainWindow.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFileDialog>
#include <QMessageBox>
#include <QLabel>
#include <QComboBox>
#include <QPushButton>

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
    // Инициализация UI
    QWidget *centralWidget = new QWidget(this);
    QVBoxLayout *mainLayout = new QVBoxLayout(centralWidget);

    // Создание элементов управления
    filterComboBox = new QComboBox(this);
    filterComboBox->addItem("Grayscale");
    filterComboBox->addItem("Sepia");

    loadButton = new QPushButton("Load Image", this);
    applyButton = new QPushButton("Apply Filter", this);
    saveButton = new QPushButton("Save Image", this);

    imageLabel = new QLabel(this);
    imageLabel->setAlignment(Qt::AlignCenter);
    imageLabel->setMinimumSize(640, 480);

    // Компоновка элементов
    QHBoxLayout *controlsLayout = new QHBoxLayout();
    controlsLayout->addWidget(loadButton);
    controlsLayout->addWidget(filterComboBox);
    controlsLayout->addWidget(applyButton);
    controlsLayout->addWidget(saveButton);

    mainLayout->addLayout(controlsLayout);
    mainLayout->addWidget(imageLabel);

    setCentralWidget(centralWidget);

    // Подключение сигналов
    connect(loadButton, &QPushButton::clicked, this, &MainWindow::loadImage);
    connect(applyButton, &QPushButton::clicked, this, &MainWindow::applyFilter);
    connect(saveButton, &QPushButton::clicked, this, &MainWindow::saveImage);
}

void MainWindow::loadImage() {
    QString fileName = QFileDialog::getOpenFileName(
        this,
        "Open Image",
        "",
        "Image Files (*.png *.jpg *.jpeg *.bmp)"
        );

    if (!fileName.isEmpty()) {
        originalImage.load(fileName);
        if (originalImage.isNull()) {
            QMessageBox::critical(this, "Error", "Failed to load image!");
            return;
        }
        processedImage = originalImage.convertToFormat(QImage::Format_ARGB32);
        updateDisplay();
    }
}

void MainWindow::applyFilter() {
    if (originalImage.isNull()) {
        QMessageBox::warning(this, "Error", "No image loaded!");
        return;
    }

    processedImage = originalImage.convertToFormat(QImage::Format_ARGB32);

    switch(filterComboBox->currentIndex()) {
    case 0: applyGrayscale(processedImage); break;
    case 1: applySepia(processedImage); break;
    default: break;
    }

    updateDisplay();
}

void MainWindow::applyGrayscale(QImage &image) {
    for (int y = 0; y < image.height(); ++y) {
        QRgb *scanLine = reinterpret_cast<QRgb*>(image.scanLine(y));
        for (int x = 0; x < image.width(); ++x) {
            int gray = qGray(scanLine[x]);
            scanLine[x] = qRgba(gray, gray, gray, qAlpha(scanLine[x]));
        }
    }
}

void MainWindow::applySepia(QImage &image) {
    for (int y = 0; y < image.height(); ++y) {
        QRgb *scanLine = reinterpret_cast<QRgb*>(image.scanLine(y));
        for (int x = 0; x < image.width(); ++x) {
            QColor color(scanLine[x]);

            int newRed = qMin(0.393 * color.red() + 0.769 * color.green() + 0.189 * color.blue(), 255.0);
            int newGreen = qMin(0.349 * color.red() + 0.686 * color.green() + 0.168 * color.blue(), 255.0);
            int newBlue = qMin(0.272 * color.red() + 0.534 * color.green() + 0.131 * color.blue(), 255.0);

            scanLine[x] = qRgba(newRed, newGreen, newBlue, color.alpha());
        }
    }
}

void MainWindow::saveImage() {
    if (processedImage.isNull()) {
        QMessageBox::warning(this, "Error", "No image to save!");
        return;
    }

    QString fileName = QFileDialog::getSaveFileName(
        this,
        "Save Image",
        "",
        "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)"
        );

    if (!fileName.isEmpty() && !processedImage.save(fileName)) {
        QMessageBox::critical(this, "Error", "Failed to save image!");
    }
}

void MainWindow::updateDisplay() {
    QPixmap pixmap = QPixmap::fromImage(processedImage);
    imageLabel->setPixmap(pixmap.scaled(
        imageLabel->size(),
        Qt::KeepAspectRatio,
        Qt::SmoothTransformation
        ));
}
