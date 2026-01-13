#include "MainWindow.h"
#include "ConcreteStrategies.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFileDialog>
#include <QLabel>
#include <QComboBox>
#include <QPushButton>
#include <QMessageBox>

MainWindow::MainWindow(QWidget* parent) : QMainWindow(parent) {
    setupUI();
    resize(800, 600);
}

void MainWindow::setupUI() {
    QWidget* centralWidget = new QWidget(this);
    QVBoxLayout* mainLayout = new QVBoxLayout(centralWidget);

    // Setup UI components
    filterComboBox = new QComboBox();
    filterComboBox->addItem("Grayscale", QVariant::fromValue(static_cast<ImageProcessingStrategy*>(new GrayscaleStrategy())));

    filterComboBox->addItem("Sepia", QVariant::fromValue(static_cast<ImageProcessingStrategy*>(new SepiaStrategy())));

    // Проверка данных
    qDebug() << "Item 0 data valid:" << filterComboBox->itemData(0).isValid();
    qDebug() << "Item 1 data valid:" << filterComboBox->itemData(1).isValid();

    loadButton = new QPushButton("Load Image");
    applyButton = new QPushButton("Apply Filter");

    imageLabel = new QLabel();
    imageLabel->setAlignment(Qt::AlignCenter);
    imageLabel->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);

    saveButton = new QPushButton("Save Image");



    // Layout
    QHBoxLayout* controlLayout = new QHBoxLayout();
    controlLayout->addWidget(loadButton);
    controlLayout->addWidget(filterComboBox);
    controlLayout->addWidget(applyButton);
    controlLayout->addWidget(saveButton);

    mainLayout->addLayout(controlLayout);
    mainLayout->addWidget(imageLabel);

    setCentralWidget(centralWidget);

    // Connect signals
    connect(loadButton, &QPushButton::clicked, this, &MainWindow::loadImage);
    connect(applyButton, &QPushButton::clicked, this, &MainWindow::applyFilter);
    connect(saveButton, &QPushButton::clicked, this, &MainWindow::saveImage);
}

void MainWindow::loadImage() {
    QString fileName = QFileDialog::getOpenFileName(
        this, "Open Image", "",
        "Image Files (*.png *.jpg *.jpeg *.bmp)"
        );

    if (!fileName.isEmpty()) {
        originalImage.load(fileName);
        if (originalImage.format() != QImage::Format_ARGB32) {
            processedImage = originalImage.convertToFormat(QImage::Format_ARGB32);
        } else {
            processedImage = originalImage.copy();
        }
        updateDisplay();
    }
}

void MainWindow::applyFilter() {
    if (!originalImage.isNull()) {
        processedImage = originalImage.copy();

        QVariant data = filterComboBox->currentData();
        qDebug() << "Raw variant type:" << data.typeName();

        if(data.canConvert<ImageProcessingStrategy*>()) {
            auto strategy = data.value<ImageProcessingStrategy*>();
            qDebug() << "Selected strategy address:" << strategy;

            if(strategy) {
                qDebug() << "Strategy type:" << typeid(*strategy).name();
                processor.setStrategy(strategy);
                processor.processImage(processedImage);
                updateDisplay();
                return;
            }
        }
        qWarning() << "Failed to get strategy!";
    }
}

void MainWindow::saveImage() {
    if (!processedImage.isNull()) {
        QString fileName = QFileDialog::getSaveFileName(
            this, "Save Image", "",
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;BMP Image (*.bmp)"
            );

        if (!fileName.isEmpty()) {
            if (!processedImage.save(fileName)) {
                QMessageBox::warning(this, "Error", "Failed to save image!");
            }
        }
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
