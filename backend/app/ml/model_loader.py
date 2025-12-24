from deepface import DeepFace
from ..config import settings
import logging
import os
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Global model cache
_model_cache = None

def preload_model():
    """Preload the model during startup to avoid timeout on first request"""
    global _model_cache
    
    logger.info(f"Preloading {settings.DEEPFACE_MODEL} model...")
    
    try:
        # Create a dummy image to force model loading
        dummy_image = np.zeros((224, 224, 3), dtype=np.uint8)
        
        # This will download and load the model
        DeepFace.represent(
            img_path=dummy_image,
            model_name=settings.DEEPFACE_MODEL,
            enforce_detection=False
        )
        
        _model_cache = True
        logger.info(f"✓ {settings.DEEPFACE_MODEL} model loaded and cached")
        return True
        
    except Exception as e:
        logger.error(f"Error preloading model: {e}")
        return False

def verify_faces(image1_path: str, image2_path: str):
    """
    Verify if two face images belong to the same person
    
    Args:
        image1_path: Path to first image
        image2_path: Path to second image
        
    Returns:
        tuple: (result, confidence_score)
            - result: "match" or "no_match"
            - confidence_score: float between 0 and 1
    """
    logger.info(f"Initialized FaceVerification with {settings.DEEPFACE_MODEL}, threshold={settings.VERIFICATION_THRESHOLD}")
    logger.info(f"Verifying faces: {image1_path} vs {image2_path}")
    
    try:
        # Verify faces using DeepFace
        result = DeepFace.verify(
            img1_path=image1_path,
            img2_path=image2_path,
            model_name=settings.DEEPFACE_MODEL,
            enforce_detection=True,
            distance_metric="cosine"
        )
        
        # Extract results
        distance = result.get("distance", 1.0)
        threshold = result.get("threshold", settings.VERIFICATION_THRESHOLD)
        is_match = result.get("verified", False)
        
        # Calculate confidence score (inverse of distance, normalized)
        # Lower distance = higher confidence
        confidence_score = max(0.0, min(1.0, 1 - (distance / threshold)))
        
        # Determine result
        verification_result = "match" if is_match else "no_match"
        
        logger.info(f"Verification result: {verification_result}")
        logger.info(f"Distance: {distance:.4f}, Threshold: {threshold:.4f}")
        logger.info(f"Confidence: {confidence_score:.4f}")
        
        return verification_result, confidence_score
        
    except Exception as e:
        logger.error(f"Face verification error: {str(e)}")
        
        # If no face detected, return no_match with low confidence
        if "Face could not be detected" in str(e):
            logger.warning("No face detected in one or both images")
            return "no_match", 0.0
        
        raise Exception(f"Verification failed: {str(e)}")