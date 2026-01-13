#include "MainWindow.h"
#include <QApplication>
#include "ImageProcessingStrategy.h"

int main(int argc, char *argv[]) {
    // Проверка регистрации типа
    qDebug() << "ImageProcessingStrategy* type ID:"
             << QMetaType::type("ImageProcessingStrategy*");

    qRegisterMetaType<ImageProcessingStrategy*>("ImageProcessingStrategy*");

    QApplication a(argc, argv);
    MainWindow w;
    w.show();
    return a.exec();
}
