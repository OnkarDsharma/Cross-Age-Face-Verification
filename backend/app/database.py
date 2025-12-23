from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from .config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    
mongodb = MongoDB()

async def connect_to_mongo():
    """Connect to MongoDB"""
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
        # Test the connection
        await mongodb.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
    except ConnectionFailure as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close MongoDB connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Closed MongoDB connection")

def get_database():
    """Get database instance"""
    return mongodb.client[settings.DATABASE_NAME]

# Collection names
USERS_COLLECTION = "users"
VERIFICATION_HISTORY_COLLECTION = "verification_history"


# ============= DATABASE OPERATIONS =============

# USER OPERATIONS
async def get_user_by_username(username: str):
    """Get user by username"""
    from .models import UserInDB
    db = get_database()
    user_dict = await db[USERS_COLLECTION].find_one({"username": username})
    if user_dict:
        return UserInDB(**user_dict)
    return None

async def get_user_by_email(email: str):
    """Get user by email"""
    from .models import UserInDB
    db = get_database()
    user_dict = await db[USERS_COLLECTION].find_one({"email": email})
    if user_dict:
        return UserInDB(**user_dict)
    return None

async def create_user(email: str, username: str, password_hash: str):
    """Create a new user"""
    from .models import UserInDB
    from datetime import datetime
    
    db = get_database()
    
    user_dict = {
        "email": email,
        "username": username,
        "password_hash": password_hash,
        "created_at": datetime.utcnow()
    }
    
    result = await db[USERS_COLLECTION].insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    
    return UserInDB(**user_dict)

async def user_exists(email: str = None, username: str = None) -> bool:
    """Check if user exists"""
    db = get_database()
    query = {}
    if email:
        query["email"] = email
    if username:
        query["username"] = username
    
    if not query:
        return False
    
    user = await db[USERS_COLLECTION].find_one(query)
    return user is not None


# VERIFICATION OPERATIONS
async def create_verification_record(user_id: str, image1_filename: str, image2_filename: str, result: str, confidence_score: float):
    """Create a new verification record"""
    from datetime import datetime
    
    db = get_database()
    
    verification_dict = {
        "user_id": user_id,
        "image1_filename": image1_filename,
        "image2_filename": image2_filename,
        "result": result,
        "confidence_score": float(confidence_score),
        "created_at": datetime.utcnow()
    }
    
    result = await db[VERIFICATION_HISTORY_COLLECTION].insert_one(verification_dict)
    verification_dict["_id"] = result.inserted_id
    
    logger.info(f"Created verification record: {result.inserted_id}")
    
    return verification_dict

async def get_user_verification_history(user_id: str, limit: int = 50):
    """Get verification history for a user"""
    db = get_database()
    
    try:
        cursor = db[VERIFICATION_HISTORY_COLLECTION].find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit)
        
        verifications = []
        async for doc in cursor:
            # Convert ObjectId to string
            doc['_id'] = str(doc['_id'])
            verifications.append(doc)
        
        logger.info(f"Retrieved {len(verifications)} verifications for user {user_id}")
        return verifications
        
    except Exception as e:
        logger.error(f"Error getting verification history: {e}")
        raise

async def delete_user_verification_history(user_id: str):
    """Delete all verifications for a user"""
    db = get_database()
    result = await db[VERIFICATION_HISTORY_COLLECTION].delete_many({"user_id": user_id})
    logger.info(f"Deleted {result.deleted_count} verifications for user {user_id}")