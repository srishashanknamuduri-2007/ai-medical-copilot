"""
Tesseract OCR Engine Invocation & Fallback Layer.
Executes pytesseract on preprocessed image arrays with configurable PSM & OEM modes.
"""

import pytesseract
import numpy as np
import logging

logger = logging.getLogger(__name__)

def run_tesseract_ocr(image: np.ndarray, psm: int = 6, oem: int = 3) -> str:
    """
    Invokes Tesseract OCR on a preprocessed NumPy image array.
    
    Args:
        image: Preprocessed grayscale/thresholded image array.
        psm: Page Segmentation Mode (default 6: Assume a single uniform block of text).
        oem: OCR Engine Mode (default 3: Default, based on what is available).
        
    Returns:
        Raw extracted text string from Tesseract.
    """
    config = f'--psm {psm} --oem {oem}'
    try:
        raw_text = pytesseract.image_to_string(image, config=config)
        return raw_text.strip()
    except Exception as e:
        logger.error(f"Tesseract OCR Execution Error: {str(e)}")
        # Return fallback text if binary is not installed in local environment
        return ""
