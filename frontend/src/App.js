import React, { useState, useRef } from 'react';
import './FaceVerification.css';

export default function FaceVerification() {
  const [image1, setImage1] = useState(null);
  const [image2, setImage2] = useState(null);
  const [preview1, setPreview1] = useState(null);
  const [preview2, setPreview2] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  // Create refs for file inputs
  const fileInput1Ref = useRef(null);
  const fileInput2Ref = useRef(null);

  const handleImageUpload = (e, setImage, setPreview) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file (PNG, JPG, JPEG)');
        return;
      }

      // Validate file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
      }

      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
      setResult(null);
    }
  };

  const clearImage = (setImage, setPreview) => {
    setImage(null);
    setPreview(null);
    setResult(null);
  };

  const handleVerify = async () => {
    if (!image1 || !image2) {
      alert('Please upload both images');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('image1', image1);
      formData.append('image2', image2);

      // FIXED: Correct endpoint is /predict, not /api/verify
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Prediction failed');
      }

      setResult(data);
    } catch (error) {
      console.error('Error:', error);
      setResult({
        error: true,
        message: error.message || 'Failed to verify images. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Face Verification System</h1>
      <p className="subtitle">Age-Invariant Person Identification using ArcFace</p>
      <p className="description">Upload two images to verify if they are of the same person</p>

      <div className="upload-section">
        <label className="upload-label">First Image</label>
        {!preview1 ? (
          <div className="upload-box" onClick={() => fileInput1Ref.current?.click()}>
            <div className="upload-icon">⬆️</div>
            <p className="upload-text">Click to upload or drag and drop</p>
            <p className="file-info">PNG, JPG up to 10MB</p>
            <button type="button" className="choose-file-btn" onClick={(e) => {
              e.stopPropagation();
              fileInput1Ref.current?.click();
            }}>
              Choose File
            </button>
            <span className="no-file-text">No file chosen</span>
            <input
              ref={fileInput1Ref}
              type="file"
              accept="image/*"
              onChange={(e) => handleImageUpload(e, setImage1, setPreview1)}
              style={{ display: 'none' }}
            />
          </div>
        ) : (
          <div className="preview-container">
            <img src={preview1} alt="Preview 1" className="preview-image" />
            <button onClick={() => clearImage(setImage1, setPreview1)} className="clear-btn">
              ✕
            </button>
          </div>
        )}
      </div>

      <div className="upload-section">
        <label className="upload-label">Second Image</label>
        {!preview2 ? (
          <div className="upload-box" onClick={() => fileInput2Ref.current?.click()}>
            <div className="upload-icon">⬆️</div>
            <p className="upload-text">Click to upload or drag and drop</p>
            <p className="file-info">PNG, JPG up to 10MB</p>
            <button type="button" className="choose-file-btn" onClick={(e) => {
              e.stopPropagation();
              fileInput2Ref.current?.click();
            }}>
              Choose File
            </button>
            <span className="no-file-text">No file chosen</span>
            <input
              ref={fileInput2Ref}
              type="file"
              accept="image/*"
              onChange={(e) => handleImageUpload(e, setImage2, setPreview2)}
              style={{ display: 'none' }}
            />
          </div>
        ) : (
          <div className="preview-container">
            <img src={preview2} alt="Preview 2" className="preview-image" />
            <button onClick={() => clearImage(setImage2, setPreview2)} className="clear-btn">
              ✕
            </button>
          </div>
        )}
      </div>

      <button 
        onClick={handleVerify} 
        disabled={!image1 || !image2 || loading}
        className="verify-btn"
      >
        {loading && <div className="spinner"></div>}
        {loading ? 'Verifying...' : 'Verify Identity'}
      </button>

      {result && (
        <div className={`result-box ${result.error ? 'error' : result.is_same_person ? 'success' : 'warning'}`}>
          <div className="result-icon">
            {result.error ? '❌' : result.is_same_person ? '✓' : '✗'}
          </div>
          <div className="result-content">
            <h3 className="result-title">
              {result.error ? 'Error' : result.is_same_person ? 'Same Person' : 'Different People'}
            </h3>
            <p className="result-message">
              {result.message || (result.error 
                ? 'An error occurred during verification.' 
                : result.is_same_person 
                  ? 'The images appear to be of the same person.' 
                  : 'The images appear to be of different people.')}
            </p>
            {result.confidence_percentage && (
              <div className="confidence-section">
                <div className="confidence-header">
                  <span className="confidence-label">Confidence Score</span>
                  <span className="confidence-value">{result.confidence_percentage.toFixed(1)}%</span>
                </div>
                <div className="confidence-bar">
                  <div 
                    className={`confidence-fill ${result.is_same_person ? 'success-fill' : 'warning-fill'}`}
                    style={{ width: `${result.confidence_percentage}%` }}
                  ></div>
                </div>
              </div>
            )}
            {result.verification_score && (
              <p className="similarity-text">
                Verification Score: {(result.verification_score * 100).toFixed(1)}%
              </p>
            )}
            {result.cosine_similarity !== undefined && (
              <p className="similarity-text">
                Cosine Similarity: {(result.cosine_similarity * 100).toFixed(1)}%
              </p>
            )}
            {result.euclidean_distance !== undefined && (
              <p className="similarity-text">
                Euclidean Distance: {result.euclidean_distance.toFixed(3)}
              </p>
            )}
          </div>
        </div>
      )}

      <div className="how-it-works">
        <h2>How It Works</h2>
        
        <div className="steps-grid">
          <div className="step-card">
            <div className="step-number">1</div>
            <h3 className="step-title">Upload Images</h3>
            <p className="step-description">Upload two face images you want to compare</p>
          </div>

          <div className="step-card">
            <div className="step-number">2</div>
            <h3 className="step-content">
              <h3 className="step-title">AI Analysis</h3>
              <p className="step-description">ArcFace model extracts and compares facial features</p>
            </h3>
          </div>

          <div className="step-card">
            <div className="step-number">3</div>
            <h3 className="step-title">Get Results</h3>
            <p className="step-description">Receive verification result with confidence score</p>
          </div>
        </div>
      </div>
    </div>
  );
}