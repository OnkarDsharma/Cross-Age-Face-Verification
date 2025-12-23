from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings
import logging
import ssl
import certifi

logger = logging.getLogger(__name__)

# Global MongoDB client
mongodb_client: AsyncIOMotorClient = None

# Collection names
USERS_COLLECTION = "users"
VERIFICATION_HISTORY_COLLECTION = "verification_history"

async def connect_to_mongo():
    """Connect to MongoDB with custom SSL context for Hugging Face Spaces"""
    global mongodb_client
    try:
        logger.info("Connecting to MongoDB...")
        logger.info(f"Database: {settings.DATABASE_NAME}")
        
        # Create custom SSL context that doesn't verify certificates
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create MongoDB client with custom SSL context
        mongodb_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            serverSelectionTimeoutMS=60000,
            connectTimeoutMS=60000,
            socketTimeoutMS=60000,
            retryWrites=True,
            w='majority',
            maxPoolSize=1,
            minPoolSize=0
        )
        
        # Test connection
        await mongodb_client.admin.command('ping')
        logger.info("✓ MongoDB connected successfully!")
        
        # Verify database exists
        db = mongodb_client[settings.DATABASE_NAME]
        collections = await db.list_collection_names()
        logger.info(f"✓ Available collections: {collections}")
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {type(e).__name__}: {e}")
        logger.error("Please check:")
        logger.error("1. MongoDB URL is correct")
        logger.error("2. Password is URL-encoded")
        logger.error("3. Network Access allows 0.0.0.0/0 in MongoDB Atlas")
        raise

async def close_mongo_connection():
    """Close MongoDB connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("✓ MongoDB connection closed")

def get_database():
    """Get MongoDB database instance"""
    return mongodb_client[settings.DATABASE_NAME]

# USER OPERATIONS
async def create_user(email: str, username: str, password_hash: str):
    """Create a new user"""
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
    
    logger.info(f"Created user: {username}")
    
    return user_dict

async def get_user_by_username(username: str):
    """Get user by username"""
    db = get_database()
    user = await db[USERS_COLLECTION].find_one({"username": username})
    return user

async def get_user_by_email(email: str):
    """Get user by email"""
    db = get_database()
    user = await db[USERS_COLLECTION].find_one({"email": email})
    return user

async def user_exists(username: str = None, email: str = None):
    """Check if user exists"""
    db = get_database()
    
    if username:
        user = await db[USERS_COLLECTION].find_one({"username": username})
        if user:
            return True
    
    if email:
        user = await db[USERS_COLLECTION].find_one({"email": email})
        if user:
            return True
    
    return False

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
    
    insert_result = await db[VERIFICATION_HISTORY_COLLECTION].insert_one(verification_dict)
    
    logger.info(f"Created verification record: {insert_result.inserted_id}")
    
    return {
        "_id": str(insert_result.inserted_id),
        "user_id": user_id,
        "image1_filename": image1_filename,
        "image2_filename": image2_filename,
        "result": result,
        "confidence_score": float(confidence_score),
        "created_at": verification_dict["created_at"]
    }

async def get_user_verification_history(user_id: str, limit: int = 50):
    """Get verification history for a user"""
    db = get_database()
    
    try:
        cursor = db[VERIFICATION_HISTORY_COLLECTION].find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit)
        
        verifications = []
        async for doc in cursor:
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