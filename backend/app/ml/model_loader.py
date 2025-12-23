from deepface import DeepFace
import logging
import os

logger = logging.getLogger(__name__)

class FaceVerificationModel:
    def __init__(self, threshold: float = 0.4, model_name: str = "Facenet512"):
        """
        Initialize DeepFace-based face verification
        
        Args:
            threshold: Distance threshold for matching (lower = stricter)
            model_name: DeepFace model to use (Facenet512, VGG-Face, ArcFace, etc.)
        """
        self.threshold = threshold
        self.model_name = model_name
        logger.info(f"Initialized FaceVerification with {model_name}, threshold={threshold}")
    
    def verify_faces(self, image1_path: str, image2_path: str):
        """
        Verify if two face images are of the same person using DeepFace
        
        Args:
            image1_path: Path to first image
            image2_path: Path to second image
            
        Returns:
            tuple: (result, confidence) where result is 'match' or 'no_match'
        """
        try:
            logger.info(f"Verifying faces: {image1_path} vs {image2_path}")
            
            # Use DeepFace to verify
            result = DeepFace.verify(
                img1_path=image1_path,
                img2_path=image2_path,
                model_name=self.model_name,
                enforce_detection=False,  # Don't fail if face detection fails
                distance_metric="cosine"
            )
            
            # Extract distance and verification result
            distance = result["distance"]
            
            # Convert distance to confidence score (0-1)
            # Lower distance = higher confidence
            # For cosine similarity, distance is typically 0-1
            confidence = 1 - min(distance, 1.0)
            confidence = max(0.0, min(1.0, confidence))
            
            # Determine result
            match_result = "match" if distance <= self.threshold else "no_match"
            
            logger.info(f"Distance: {distance:.4f}, Confidence: {confidence:.4f}, Threshold: {self.threshold}")
            logger.info(f"Result: {match_result} (distance {'<=' if distance <= self.threshold else '>'} threshold)")
            
            return match_result, float(confidence)
            
            
        except Exception as e:
            logger.error(f"Error during face verification: {e}")
            logger.warning("Verification failed, returning no_match")
            return "no_match", 0.0


# Global model instance
_model_instance = None

def get_model(threshold: float = None, model_name: str = None):
    """Get or create the model instance"""
    global _model_instance
    
    if _model_instance is None:
        from ..config import settings
        
        threshold = threshold or settings.VERIFICATION_THRESHOLD
        model_name = model_name or getattr(settings, 'DEEPFACE_MODEL', 'Facenet512')
        
        _model_instance = FaceVerificationModel(threshold, model_name)
    
    return _model_instance



def verify_faces(image1_path: str, image2_path: str):
    """
    Convenience function to verify faces using the global model instance
    """
    model = get_model()
    return model.verify_faces(image1_path, image2_path)
