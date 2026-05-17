from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from PIL import Image
import io
from typing import Optional
from ..application.dtos.vision_dtos import (
    TaskType,
    DetectionResponseDTO as DetectionResponse,
    CaptionResponseDTO as CaptionResponse,
    OCRResponseDTO as OCRResponse,
)
from ..core.dependencies import get_yolo, get_blip, get_easyocr
from ..core.config import get_settings
from ..models.yolo_detector import YOLODetector
from ..models.blip_captioner import BLIPCaptioner
from ..models.easy_ocr import EasyOCRProcessor

router = APIRouter(prefix="/vision", tags=["vision"])


async def load_image(file: UploadFile) -> Image.Image:
    settings = get_settings()
    contents = await file.read()
    if len(contents) > settings.MAX_IMAGE_SIZE:
        raise HTTPException(400, f"Image too large (max {settings.MAX_IMAGE_SIZE // 1024 // 1024}MB)")
    try:
        return Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(400, "Invalid image file")


@router.post("/detect", response_model=DetectionResponse)
async def detect_objects(
    file: UploadFile = File(...),
    conf: float = 0.25,
    detector: YOLODetector = Depends(get_yolo)
):
    image = await load_image(file)
    return await detector.detect(image, conf_threshold=conf)


@router.post("/caption", response_model=CaptionResponse)
async def caption_image(
    file: UploadFile = File(...),
    captioner: BLIPCaptioner = Depends(get_blip)
):
    image = await load_image(file)
    return await captioner.caption(image)


@router.post("/ocr", response_model=OCRResponse)
async def extract_text(
    file: UploadFile = File(...),
    ocr: EasyOCRProcessor = Depends(get_easyocr),
    engine: str = "easyocr"
):
    image = await load_image(file)
    return await ocr.extract_text(image, engine=engine)


@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    task: TaskType = TaskType.CAPTION_IMAGE,
    detector: YOLODetector = Depends(get_yolo),
    captioner: BLIPCaptioner = Depends(get_blip),
    ocr: EasyOCRProcessor = Depends(get_easyocr)
):
    image = await load_image(file)

    if task == TaskType.DETECT_OBJECTS:
        return await detector.detect(image)
    elif task == TaskType.CAPTION_IMAGE:
        return await captioner.caption(image)
    elif task == TaskType.EXTRACT_TEXT:
        return await ocr.extract_text(image)
    else:
        return {
            "caption": await captioner.caption(image),
            "detections": await detector.detect(image),
            "ocr": await ocr.extract_text(image)
        }
