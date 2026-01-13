// ConcreteStrategies.h (исправленные реализации фильтров)
#ifndef CONCRETESTRATEGIES_H
#define CONCRETESTRATEGIES_H

#include "ImageProcessingStrategy.h"
#include <QDebug>

class GrayscaleStrategy : public ImageProcessingStrategy {
public:
    void applyFilter(QImage& image) const override {
        // Работаем непосредственно с переданным изображением
        if(image.format() != QImage::Format_ARGB32) {
            qWarning() << "Converting image format to ARGB32 in filter";
            image = image.convertToFormat(QImage::Format_ARGB32);
        }

        for(int y = 0; y < image.height(); ++y) {
            QRgb* scanLine = reinterpret_cast<QRgb*>(image.scanLine(y));
            for(int x = 0; x < image.width(); ++x) {
                QRgb pixel = scanLine[x];
                int gray = qGray(pixel);
                scanLine[x] = qRgba(gray, gray, gray, qAlpha(pixel));
            }
        }
    }
};

class SepiaStrategy : public ImageProcessingStrategy {
public:
    void applyFilter(QImage& image) const override {
        if(image.format() != QImage::Format_ARGB32) {
            image = image.convertToFormat(QImage::Format_ARGB32);
        }

        for(int y = 0; y < image.height(); ++y) {
            QRgb* scanLine = reinterpret_cast<QRgb*>(image.scanLine(y));
            for(int x = 0; x < image.width(); ++x) {
                QColor color(scanLine[x]);

                int newRed = qMin(0.393 * color.red() + 0.769 * color.green() + 0.189 * color.blue(), 255.0);
                int newGreen = qMin(0.349 * color.red() + 0.686 * color.green() + 0.168 * color.blue(), 255.0);
                int newBlue = qMin(0.272 * color.red() + 0.534 * color.green() + 0.131 * color.blue(), 255.0);

                scanLine[x] = qRgba(newRed, newGreen, newBlue, color.alpha());
            }
        }
    }
};

#endif // CONCRETESTRATEGIES_H
