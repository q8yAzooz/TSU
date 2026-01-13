#ifndef IMAGEPROCESSINGSTRATEGY_H
#define IMAGEPROCESSINGSTRATEGY_H

#include <QImage>
#include <QMetaType>

class ImageProcessingStrategy {
public:
    virtual ~ImageProcessingStrategy() = default;
    virtual void applyFilter(QImage& image) const = 0;
};

Q_DECLARE_METATYPE(ImageProcessingStrategy*)

#endif // IMAGEPROCESSINGSTRATEGY_H
