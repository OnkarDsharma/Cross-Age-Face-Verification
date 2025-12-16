from flask import Flask, request, jsonify
from flask_cors import CORS
from deepface import DeepFace
import os
import io
from werkzeug.utils import secure_filename
import traceback
from PIL import Image
import numpy as np
import cv2

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MODEL_NAME = 'Facenet512'  # The model you're using
THRESHOLD = 0.498  # Distance threshold (lower = more similar)
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Global variables
model_loaded = False


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def initialize_deepface():
    """Initialize DeepFace model by running a test"""
    global model_loaded
    try:
        print("🔄 Initializing DeepFace model...")
        print("   This may take a few minutes on first run (downloading model weights)...")
        
        # Create a temporary dummy image to test the model
        temp_img_path = os.path.join(UPLOAD_FOLDER, 'temp_init.jpg')
        dummy_img = np.ones((160, 160, 3), dtype=np.uint8) * 128
        cv2.imwrite(temp_img_path, dummy_img)
        
        try:
            # Test the model with the dummy image
            _ = DeepFace.represent(
                img_path=temp_img_path,
                model_name=MODEL_NAME,
                enforce_detection=False
            )
            print("✓ DeepFace model initialized successfully!")
            model_loaded = True
            return True
        finally:
            # Clean up temp file
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
        
    except Exception as e:
        print(f"✗ Error initializing DeepFace: {str(e)}")
        print("\n💡 Common issues:")
        print("   1. First run downloads ~100MB of model weights - this is normal")
        print("   2. Make sure you have internet connection for first run")
        print("   3. Try: pip install --upgrade deepface tensorflow")
        traceback.print_exc()
        model_loaded = False
        return False


def save_temp_image(image_file, filename):
    """Save uploaded image temporarily"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        return filepath
    except Exception as e:
        raise Exception(f"Error saving image: {str(e)}")


def verify_faces(img1_path, img2_path):
    """
    Verify if two faces belong to the same person using DeepFace
    Returns similarity metrics
    """
    try:
        # Perform face verification using DeepFace
        result = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            model_name=MODEL_NAME,
            enforce_detection=False  # Don't enforce face detection to handle edge cases
        )
        
        # Extract results
        distance = result['distance']
        is_same_person = distance <= THRESHOLD
        
        # Calculate confidence (inverse of distance, normalized)
        # Lower distance = higher confidence
        confidence = max(0, min(1, 1 - (distance / 1.0)))
        confidence_percentage = confidence * 100
        
        # Calculate similarity score (0-1 range)
        similarity = max(0, 1 - distance)
        
        return {
            'is_same_person': bool(is_same_person),
            'distance': float(distance),
            'threshold': float(THRESHOLD),
            'confidence': float(confidence),
            'confidence_percentage': float(confidence_percentage),
            'similarity': float(similarity),
            'model': MODEL_NAME,
            'verified': result.get('verified', is_same_person)
        }
    
    except Exception as e:
        raise Exception(f"Face verification error: {str(e)}")


# ============= API ENDPOINTS =============

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Age-Invariant Face Verification API',
        'status': 'running',
        'model_loaded': model_loaded,
        'model': MODEL_NAME,
        'threshold': THRESHOLD,
        'endpoints': {
            'health': 'GET /health',
            'predict': 'POST /predict',
            'model_info': 'GET /model-info'
        }
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Backend is running',
        'model_loaded': model_loaded,
        'model': MODEL_NAME,
        'threshold': THRESHOLD
    }), 200


@app.route('/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    img1_path = None
    img2_path = None
    
    try:
        # Validate request
        if 'image1' not in request.files or 'image2' not in request.files:
            return jsonify({
                'error': 'Both image1 and image2 are required',
                'usage': 'Send two images as multipart/form-data with keys "image1" and "image2"'
            }), 400
        
        image1 = request.files['image1']
        image2 = request.files['image2']
        
        # Check if files are selected
        if image1.filename == '' or image2.filename == '':
            return jsonify({
                'error': 'No files selected. Please select both images.'
            }), 400
        
        # Validate file types
        if not (allowed_file(image1.filename) and allowed_file(image2.filename)):
            return jsonify({
                'error': f'Invalid file format. Allowed formats: {", ".join(ALLOWED_EXTENSIONS).upper()}'
            }), 400
        
        # Save images temporarily
        print(f"Processing images: {image1.filename}, {image2.filename}")
        img1_path = save_temp_image(image1, secure_filename(f"temp_img1_{image1.filename}"))
        img2_path = save_temp_image(image2, secure_filename(f"temp_img2_{image2.filename}"))
        
        # Verify faces
        result = verify_faces(img1_path, img2_path)
        
        # Add user-friendly message
        if result['is_same_person']:
            result['message'] = f"✓ Same Person (Confidence: {result['confidence_percentage']:.1f}%)"
            result['status'] = 'match'
        else:
            result['message'] = f"✗ Different Persons (Distance: {result['distance']:.3f})"
            result['status'] = 'no_match'
        
        print(f"Prediction result: {result['message']}")
        
        return jsonify(result), 200
    
    except Exception as e:
        print(f"Error in predict endpoint: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': f'Prediction failed: {str(e)}',
            'details': 'Check server logs for more information'
        }), 500
    
    finally:
        # Clean up temporary files
        try:
            if img1_path and os.path.exists(img1_path):
                os.remove(img1_path)
            if img2_path and os.path.exists(img2_path):
                os.remove(img2_path)
        except Exception as e:
            print(f"Error cleaning up temp files: {str(e)}")


@app.route('/model-info', methods=['GET'])
def model_info():
    """Get information about the loaded model"""
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        return jsonify({
            'model_loaded': True,
            'model_name': MODEL_NAME,
            'model_type': 'DeepFace - Facenet512',
            'threshold': THRESHOLD,
            'description': 'Age-invariant face verification using DeepFace library with Facenet512',
            'input_size': 'Variable (auto-detected by DeepFace)',
            'output': 'Distance metric (lower = more similar)',
            'threshold_info': f'Faces with distance <= {THRESHOLD} are considered same person',
            'backend': 'DeepFace with Facenet512'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': {
            'home': 'GET /',
            'health': 'GET /health',
            'predict': 'POST /predict',
            'model_info': 'GET /model-info'
        }
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


# ============= MAIN =============

if __name__ == '__main__':
    print("=" * 60)
    print("Age-Invariant Face Verification Backend Server")
    print("=" * 60)
    print("\nModel Details:")
    print(f"  - Framework: DeepFace")
    print(f"  - Model: {MODEL_NAME}")
    print(f"  - Threshold: {THRESHOLD}")
    print(f"  - Input: Two RGB face images")
    print(f"  - Output: Distance metric (lower = more similar)")
    print("=" * 60)
    
    # Initialize DeepFace model
    print("\n🔄 Loading DeepFace...")
    print("⚠️  Note: First run will download model weights (~100MB)")
    print("    This may take 2-5 minutes depending on your internet speed\n")
    
    if initialize_deepface():
        print("\n" + "=" * 60)
        print("✅ SERVER READY!")
        print("=" * 60)
        print(f"\n📡 API Endpoints:")
        print(f"  • Home:       http://localhost:5000/")
        print(f"  • Health:     http://localhost:5000/health")
        print(f"  • Predict:    http://localhost:5000/predict (POST)")
        print(f"  • Model Info: http://localhost:5000/model-info")
        print("=" * 60)
        print("\n🚀 Starting Flask server...\n")
        
        # Run Flask app
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    else:
        print("\n" + "=" * 60)
        print("❌ MODEL INITIALIZATION FAILED")
        print("=" * 60)
        print("\n🔧 Troubleshooting steps:")
        print("\n1. Verify installations:")
        print("   pip install --upgrade deepface tensorflow opencv-python")
        print("\n2. Check if you have internet connection (for first-time model download)")
        print("\n3. Test DeepFace manually:")
        print("   python -c \"from deepface import DeepFace; print('OK')\"")
        print("\n4. If still failing, try:")
        print("   pip uninstall deepface tensorflow")
        print("   pip install deepface tensorflow==2.15.0")
        print("\n5. Server will still start but predictions will fail.")
        print("   You can try to use the API anyway - it might work!")
        print("=" * 60)
        
        # Start server anyway to allow testing
        print("\n⚠️  Starting server in degraded mode...")
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)