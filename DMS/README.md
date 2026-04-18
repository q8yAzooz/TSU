# Driver Monitoring System (DMS)

Система мониторинга состояния водителя на основе компьютерного зрения. Две реализации: OpenCV (каскады Хаара) и MediaPipe (Face Landmarker).

## Возможности

- Детекция лица и глаз в реальном времени
- Подсчет морганий
- Расчет PERCLOS (процент времени с закрытыми глазами)
- Визуализация состояния
- Предупреждения о сонливости
- Сохранение скриншотов

## Установка

1. Клонировать репозиторий
2. Установить зависимости: `pip install -r requirements.txt`
3. Для MediaPipe скачать модель: [face_landmarker.task](https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task)

## Использование

**OpenCV:**

```bash
python DMS.py
```


**MediaPipe:**

```
python DMSmediapipe.py
```

## Управление

| Клавиша | Действие              |
| -------------- | ----------------------------- |
| Q              | Выход                    |
| R              | Сброс счетчиков |
| S              | Скриншот              |
| +/-            | Порог EAR (MediaPipe)    |

## Требования

* Python 3.8+
* Веб-камера
* MediaPipe модель (для второй версии)
