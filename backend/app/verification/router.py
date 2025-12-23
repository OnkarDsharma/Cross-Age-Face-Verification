from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import List , Dict, Any
import shutil
from pathlib import Path
import uuid
import logging
from ..schemas import VerificationResult
from ..models import UserInDB, VerificationResponse
from ..auth.utils import get_current_user
from ..database import create_verification_record, get_user_verification_history, delete_user_verification_history
from ..ml.model_loader import verify_faces
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/verify", tags=["verification"])

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = settings.MAX_FILE_SIZE

def validate_image(file: UploadFile):
    """Validate uploaded image"""
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

@router.post("/", response_model=VerificationResult)
async def verify_images(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    """Verify if two face images belong to the same person"""
    validate_image(image1)
    validate_image(image2)
    
    user_id = str(current_user.id)
    unique_id = str(uuid.uuid4())
    
    image1_ext = Path(image1.filename).suffix
    image2_ext = Path(image2.filename).suffix
    
    image1_filename = f"{user_id}_{unique_id}_1{image1_ext}"
    image2_filename = f"{user_id}_{unique_id}_2{image2_ext}"
    
    image1_path = UPLOAD_DIR / image1_filename
    image2_path = UPLOAD_DIR / image2_filename
    
    try:
        # Save uploaded files
        with open(image1_path, "wb") as buffer:
            shutil.copyfileobj(image1.file, buffer)
        
        with open(image2_path, "wb") as buffer:
            shutil.copyfileobj(image2.file, buffer)
        
        logger.info(f"Verifying faces for user {user_id}")
        
        # Perform verification
        result, confidence = verify_faces(str(image1_path), str(image2_path))
        
        # Save to database
        verification_record = await create_verification_record(
            user_id=user_id,
            image1_filename=image1_filename,
            image2_filename=image2_filename,
            result=result,
            confidence_score=confidence
        )
        
        message = (
            f"Same person detected! (Confidence: {confidence:.2%})" 
            if result == "match" 
            else f"Different persons detected. (Confidence: {confidence:.2%})"
        )
        
        logger.info(f"Verification complete: {result}, confidence: {confidence:.4f}")
        
        # Return proper response
        return VerificationResult(
            result=result,
            confidence_score=confidence,
            message=message,
            verification_id=str(verification_record["_id"])  # Fix: Access _id from dict
        )
        
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        # Clean up files on error
        if image1_path.exists():
            image1_path.unlink()
        if image2_path.exists():
            image2_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )

@router.get("/history")
async def get_history(
    limit: int = 50,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get verification history for current user"""
    try:
        user_id = str(current_user.id)
        logger.info(f"Fetching history for user: {user_id}")
        
        history = await get_user_verification_history(user_id, limit)
        logger.info(f"Found {len(history)} verification records")
        
        return history
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}"
        )

@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history(current_user: UserInDB = Depends(get_current_user)):
    """Delete all verification history for current user"""
    user_id = str(current_user.id)
    await delete_user_verification_history(user_id)
    return None

@router.get("/config")
async def get_config(current_user: UserInDB = Depends(get_current_user)):
    """Get current verification configuration"""
    return {
        "threshold": settings.VERIFICATION_THRESHOLD,
        "allowed_extensions": list(ALLOWED_EXTENSIONS),
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024)
    }