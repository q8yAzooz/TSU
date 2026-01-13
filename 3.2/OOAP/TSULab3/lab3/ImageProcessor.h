#ifndef IMAGEPROCESSOR_H
#define IMAGEPROCESSOR_H

#include "ImageProcessingStrategy.h"

class ImageProcessor {
    ImageProcessingStrategy* strategy = nullptr;

public:
    void setStrategy(ImageProcessingStrategy* newStrategy) {
        strategy = newStrategy;
    }

    void processImage(QImage& image) const {
        if (strategy) {
            strategy->applyFilter(image);
        }
    }
};

#endif // IMAGEPROCESSOR_H
