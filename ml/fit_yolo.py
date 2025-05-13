import cv2
import torch
from ultralytics import YOLO  # Используем YOLOv8 для детекции объектов
import easyocr  # Библиотека для распознавания текста
from roboflow import Roboflow

rf = Roboflow(api_key="5pXFfA6Z3uRGVkNdeUMD")
project = rf.workspace("roboflow-universe-projects").project("license-plate-recognition-rxg4e")
version = project.version(4)
dataset = version.download("yolov8")

# Загрузка предобученной модели YOLOv8
model = YOLO('yolov8n.pt')

# Обучение модели
results = model.train(data=f"{dataset.location}/data.yaml", epochs=10, imgsz=640, device='cuda')