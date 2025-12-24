"""
Lightweight face verification using face_recognition library
This uses dlib instead of TensorFlow - much lighter on memory!
"""
import face_recognition
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def preload_model():
    """
    Preload is not needed for face_recognition library
    It's lightweight and loads instantly
    """
    logger.info("Using face_recognition library (dlib-based)")
    logger.info("✓ No preloading needed - library is lightweight")
    return True

def verify_faces(image1_path: str, image2_path: str, threshold: float = 0.6):
    """
    Verify if two face images belong to the same person using face_recognition
    
    Args:
        image1_path: Path to first image
        image2_path: Path to second image
        threshold: Distance threshold (default 0.6, lower = stricter)
        
    Returns:
        tuple: (result, confidence_score)
            - result: "match" or "no_match"
            - confidence_score: float between 0 and 1
    """
    logger.info(f"Verifying faces: {image1_path} vs {image2_path}")
    
    try:
        # Load images
        image1 = face_recognition.load_image_file(image1_path)
        image2 = face_recognition.load_image_file(image2_path)
        
        # Get face encodings
        encodings1 = face_recognition.face_encodings(image1)
        encodings2 = face_recognition.face_encodings(image2)
        
        # Check if faces were detected
        if len(encodings1) == 0:
            logger.warning(f"No face detected in {image1_path}")
            return "no_match", 0.0
            
        if len(encodings2) == 0:
            logger.warning(f"No face detected in {image2_path}")
            return "no_match", 0.0
        
        # Use the first face from each image
        encoding1 = encodings1[0]
        encoding2 = encodings2[0]
        
        # Calculate face distance (lower = more similar)
        face_distance = face_recognition.face_distance([encoding1], encoding2)[0]
        
        # Convert distance to confidence score
        # Distance ranges from 0 (identical) to ~1.2 (very different)
        # We normalize to 0-1 where 1 is high confidence match
        confidence_score = max(0.0, min(1.0, 1 - (face_distance / 1.2)))
        
        # Determine match
        is_match = face_distance < threshold
        result = "match" if is_match else "no_match"
        
        logger.info(f"Verification result: {result}")
        logger.info(f"Face distance: {face_distance:.4f}, Threshold: {threshold:.4f}")
        logger.info(f"Confidence: {confidence_score:.4f}")
        
        return result, confidence_score
        
    except Exception as e:
        logger.error(f"Face verification error: {str(e)}")
        raise Exception(f"Verification failed: {str(e)}")