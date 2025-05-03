from fastapi import APIRouter, UploadFile, File

router = APIRouter(prefix="/ml", tags=["ML-модуль"])

@router.post("/detect-license-plate")
async def detect_license_plate(file: UploadFile = File(...)):
    """
    Эндпоинт для определения номера машины с картинки.
    """
    # Заглушка
    return {"message": "License plate detection is not implemented yet."}

@router.post("/recognize-license-plate")
async def recognize_license_plate(file: UploadFile = File(...)):
    """
    Эндпоинт для распознавания номера машины.
    """
    # Заглушка
    return {"message": "License plate recognition is not implemented yet."}