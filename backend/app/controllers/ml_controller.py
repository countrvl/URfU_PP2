from fastapi import APIRouter, UploadFile, File
import cv2
from ultralytics import YOLO
import tempfile

model = YOLO("/app/best.pt")

def detect_license_plate(image_path, model):
    image = cv2.imread(image_path)
    results = model(image)
    for result in results:
        boxes = result.boxes.data.tolist()
        for box in boxes:
            x1, y1, x2, y2, score, class_id = box
            if int(class_id) == 0:
                return int(x1), int(y1), int(x2), int(y2), score
    return None

def preprocess_license_plate(image, bbox):
    x1, y1, x2, y2 = bbox
    plate_image = image[y1:y2, x1:x2]
    gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray, 64, 255, cv2.THRESH_BINARY_INV)
    blurred = cv2.GaussianBlur(thresholded, (3, 3), 0)
    return blurred

def recognize_text(image):
    reader = easyocr.Reader(['ru'], gpu=True)
    results = reader.readtext(image)
    for detection in results:
        bbox, text, score = detection
        text = text.upper().replace(' ', '')
        return text, score
    return None, None

router = APIRouter(prefix="/ml", tags=["ML-модуль"])

@router.post("/detect-license-plate")
async def detect_license_plate(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name

    bbox = detect_license_plate(temp_file_path, model)
    if bbox is None:
        return {"message": "Номерной знак не найден"}

    x1, y1, x2, y2, score = bbox
    return {
        "bbox_2d": [x1, y1, x2, y2],
        "score": score,
        "label": "license_plate"
    }

@router.post("/recognize-license-plate")
async def recognize_license_plate(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name

    bbox = detect_license_plate(temp_file_path, model)
    if bbox is None:
        return {"message": "Номерной знак не найден"}

    image = cv2.imread(temp_file_path)
    processed_image = preprocess_license_plate(image, bbox)
    text, score = recognize_text(processed_image)
    if text is None:
        return {"message": "Текст на номерном знаке не распознан"}

    return {
        "license_plate": text,
        "confidence": score
    }