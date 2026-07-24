"""
OpenCV Image Preprocessing Pipeline for Medical Prescription OCR.
Contains modular functions for grayscale, denoising, thresholding, sharpening, and deskewing.
"""

import cv2
import numpy as np

def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Converts input BGR image to single-channel Grayscale."""
    if len(image.shape) == 3 and image.shape[2] == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def denoise_image(image: np.ndarray, h: float = 10.0) -> np.ndarray:
    """Applies Non-Local Means Denoising to reduce noise while preserving handwritten edges."""
    if len(image.shape) == 2:
        return cv2.fastNlMeansDenoising(image, None, h=h, templateWindowSize=7, searchWindowSize=21)
    return cv2.fastNlMeansDenoisingColored(image, None, h=h, hColor=h, templateWindowSize=7, searchWindowSize=21)

def adaptive_thresholding(image: np.ndarray, method: str = 'gaussian') -> np.ndarray:
    """
    Applies adaptive binarization for high-contrast handwriting extraction.
    Supports 'gaussian' or 'otsu'.
    """
    gray = to_grayscale(image)
    if method == 'otsu':
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
    else:
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 11
        )

def sharpen_image(image: np.ndarray) -> np.ndarray:
    """Applies an unsharp mask kernel to enhance contrast around handwritten text strokes."""
    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ], dtype=np.float32)
    return cv2.filter2D(image, -1, kernel)

def deskew_image(image: np.ndarray) -> np.ndarray:
    """
    Detects document orientation angle using minAreaRect on text contours and rotates the image straight.
    """
    gray = to_grayscale(image)
    # Invert image for contour detection (white text on black background)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # Find all non-zero coordinates
    coords = np.column_stack(np.where(thresh > 0))
    if coords.shape[0] == 0:
        return image
        
    angle = cv2.minAreaRect(coords)[-1]
    
    # Adjust angle range
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
        
    # Rotate only if significant skew detected (> 0.5 degrees)
    if abs(angle) > 0.5:
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
        
    return image

def preprocess_pipeline(image_bytes: bytes) -> np.ndarray:
    """
    Runs full sequential preprocessing pipeline:
    Decode -> Grayscale -> Denoise -> Deskew -> Sharpen -> Adaptive Threshold
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image from provided byte stream.")

    gray = to_grayscale(img)
    denoised = denoise_image(gray)
    deskewed = deskew_image(denoised)
    sharpened = sharpen_image(deskewed)
    thresh = adaptive_thresholding(sharpened, method='gaussian')
    
    return thresh
