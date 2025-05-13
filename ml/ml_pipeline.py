import cv2
import torch
from ultralytics import YOLO  # Используем YOLOv8 для детекции объектов
import easyocr  # Библиотека для распознавания текста
import os
import numpy as np
from roboflow import Roboflow

# Обнаружение номерной таблички
# Возвращает координаты bounding box
def detect_license_plate(image_path, model):
    # Загружаем изображение
    image = cv2.imread(image_path)

    # Используем модель для предсказания
    results = model(image)

    # Получаем координаты bounding box'а
    for result in results:
        boxes = result.boxes.data.tolist()
        for box in boxes:
            x1, y1, x2, y2, score, class_id = box
            if int(class_id) == 0:  # Предполагаем, что класс 0 - это номерная табличка
                return int(x1), int(y1), int(x2), int(y2), score

    return None  # Если номерная табличка не найдена

# Обрезка и улучшение качества изображения номерной таблички
def preprocess_license_plate(image, bbox):
    x1, y1, x2, y2 = bbox

    # Обрезка изображения по координатам bounding box'а
    plate_image = image[y1:y2, x1:x2]

    # Преобразование в градации серого
    gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)

    # Повышение контраста с помощью адаптивного порога
    _, thresholded = cv2.threshold(gray, 64, 255, cv2.THRESH_BINARY_INV)

    # Улучшение качества с помощью размытия
    blurred = cv2.GaussianBlur(thresholded, (3, 3), 0)

    return blurred

# Распознавание текста с помощью EasyOCR
def recognize_text(image):
    reader = easyocr.Reader(['ru'], gpu=True)  # Инициализация OCR
    results = reader.readtext(image)

    # Обработка результатов
    for detection in results:
        bbox, text, score = detection
        text = text.upper().replace(' ', '')  # Очистка текста
        return text, score

    return None, None

# Полный пайплайн обработки изображения
# 1. Обнаружение номерной таблички
# 2. Улучшение качества изображения
# 3. Распознавание текста
def pipline_image(image_path):
    # Загрузка обученной модели YOLOv8
    model = YOLO('./runs/detect/train/weights/best.pt')

    # Обнаружение номерной таблички
    bbox = detect_license_plate(image_path, model)
    if bbox is None:
        print("\nНомерная табличка не найдена\n")
        return

    x1, y1, x2, y2, score = bbox
    print(f"\nНомерная табличка найдена с координатами: ({x1}, {y1}, {x2}, {y2}), уверенность: {score:.3f}\n")

    # Улучшение качества изображения
    image = cv2.imread(image_path)
    processed_image = preprocess_license_plate(image, (x1, y1, x2, y2))

    # Сохранение обработанного изображения для проверки
    cv2.imwrite('processed_plate.jpg', processed_image)
    print("\nОбработанное изображение номерной таблички сохранено\n")

    # Шаг 3: Распознавание текста
    text, text_score = recognize_text(processed_image)
    if text is not None:
        print(f"\nРаспознанный текст: {text}, уверенность: {text_score:.3f}\n")
    else:
        print("\nТекст не распознан\n")


#from google.colab import files

#uploaded = files.upload()

# Тестирование
#if uploaded:
#    for img_name in uploaded.keys():
#      img_path = img_name
#      if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
#        pipline_image(img_path)
#      else:
#        print("Неподдерживаемый формат")
#else:
#    print("Картинка не была загружена")