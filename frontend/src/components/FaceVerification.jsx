import React, { useState } from 'react';
import { verifyFaces } from '../services/api';

function FaceVerification() {
  const [image1, setImage1] = useState(null);
  const [image2, setImage2] = useState(null);
  const [preview1, setPreview1] = useState(null);
  const [preview2, setPreview2] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleImage1Change = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage1(file);
      setPreview1(URL.createObjectURL(file));
      setResult(null);
      setError('');
    }
  };

  const handleImage2Change = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage2(file);
      setPreview2(URL.createObjectURL(file));
      setResult(null);
      setError('');
    }
  };

  const handleVerify = async () => {
    if (!image1 || !image2) {
      setError('Please upload both images');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await verifyFaces(image1, image2);
      setResult(response);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Verification failed';
      setError(errorMessage);
      console.error('Verification error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setImage1(null);
    setImage2(null);
    setPreview1(null);
    setPreview2(null);
    setResult(null);
    setError('');
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Cross-Age Face Verification</h2>
      <p style={styles.subtitle}>Upload two face images to verify if they belong to the same person</p>

      <div style={styles.uploadSection}>
        <div style={styles.uploadBox}>
          <h3 style={styles.uploadTitle}>Image 1</h3>
          {preview1 ? (
            <div style={styles.previewContainer}>
              <img src={preview1} alt="Preview 1" style={styles.preview} />
              <button onClick={() => {
                setImage1(null);
                setPreview1(null);
              }} style={styles.removeBtn}>✕</button>
            </div>
          ) : (
            <label style={styles.uploadLabel}>
              <input
                type="file"
                accept="image/*"
                onChange={handleImage1Change}
                style={styles.fileInput}
              />
              <div style={styles.uploadPlaceholder}>
                <span style={styles.uploadIcon}>📷</span>
                <span>Click to upload</span>
              </div>
            </label>
          )}
        </div>

        <div style={styles.uploadBox}>
          <h3 style={styles.uploadTitle}>Image 2</h3>
          {preview2 ? (
            <div style={styles.previewContainer}>
              <img src={preview2} alt="Preview 2" style={styles.preview} />
              <button onClick={() => {
                setImage2(null);
                setPreview2(null);
              }} style={styles.removeBtn}>✕</button>
            </div>
          ) : (
            <label style={styles.uploadLabel}>
              <input
                type="file"
                accept="image/*"
                onChange={handleImage2Change}
                style={styles.fileInput}
              />
              <div style={styles.uploadPlaceholder}>
                <span style={styles.uploadIcon}>📷</span>
                <span>Click to upload</span>
              </div>
            </label>
          )}
        </div>
      </div>

      <div style={styles.buttonGroup}>
        <button
          onClick={handleVerify}
          disabled={loading || !image1 || !image2}
          style={{
            ...styles.verifyBtn,
            opacity: (loading || !image1 || !image2) ? 0.6 : 1,
            cursor: (loading || !image1 || !image2) ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? '🔄 Verifying...' : '✓ Verify Faces'}
        </button>
        
        <button onClick={handleReset} style={styles.resetBtn}>
          🔄 Reset
        </button>
      </div>

      {loading && (
        <div style={styles.loadingBox}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>
            <strong>Processing your verification...</strong>
          </p>
          <p style={styles.loadingSubtext}>
            This may take up to 2 minutes on first use while loading the AI model. 
            Subsequent verifications will be much faster!
          </p>
        </div>
      )}

      {error && (
        <div style={styles.error}>
          <strong>⚠ Error:</strong> {error}
        </div>
      )}

      {result && (
        <div style={{
          ...styles.result,
          background: result.result === 'match' ? '#d4edda' : '#f8d7da',
          borderColor: result.result === 'match' ? '#c3e6cb' : '#f5c6cb'
        }}>
          <h3 style={styles.resultTitle}>
            {result.result === 'match' ? '✓ Match Found!' : '✗ No Match'}
          </h3>
          <p style={styles.resultText}>{result.message}</p>
          <div style={styles.confidence}>
            <strong>Confidence Score:</strong> {(result.confidence_score * 100).toFixed(2)}%
          </div>
          <div style={styles.progressBar}>
            <div style={{
              ...styles.progressFill,
              width: `${result.confidence_score * 100}%`,
              background: result.result === 'match' ? '#28a745' : '#dc3545'
            }} />
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '30px',
  },
  title: {
    textAlign: 'center',
    color: '#333',
    marginBottom: '10px',
    fontSize: '28px',
  },
  subtitle: {
    textAlign: 'center',
    color: '#666',
    marginBottom: '30px',
    fontSize: '16px',
  },
  uploadSection: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '30px',
    marginBottom: '30px',
  },
  uploadBox: {
    border: '2px dashed #ddd',
    borderRadius: '10px',
    padding: '20px',
    textAlign: 'center',
    background: 'white',
  },
  uploadTitle: {
    marginTop: 0,
    marginBottom: '15px',
    color: '#555',
    fontSize: '18px',
  },
  uploadLabel: {
    display: 'block',
    cursor: 'pointer',
  },
  fileInput: {
    display: 'none',
  },
  uploadPlaceholder: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '200px',
    color: '#999',
  },
  uploadIcon: {
    fontSize: '48px',
    marginBottom: '10px',
  },
  previewContainer: {
    position: 'relative',
  },
  preview: {
    width: '100%',
    maxHeight: '300px',
    objectFit: 'contain',
    borderRadius: '8px',
  },
  removeBtn: {
    position: 'absolute',
    top: '10px',
    right: '10px',
    background: '#dc3545',
    color: 'white',
    border: 'none',
    borderRadius: '50%',
    width: '30px',
    height: '30px',
    cursor: 'pointer',
    fontSize: '18px',
    fontWeight: 'bold',
  },
  buttonGroup: {
    display: 'flex',
    gap: '15px',
    justifyContent: 'center',
    marginBottom: '30px',
  },
  verifyBtn: {
    padding: '15px 40px',
    background: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.3s',
  },
  resetBtn: {
    padding: '15px 40px',
    background: '#6c757d',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  loadingBox: {
    background: '#e7f3ff',
    border: '2px solid #2196F3',
    borderRadius: '10px',
    padding: '30px',
    textAlign: 'center',
    marginBottom: '20px',
  },
  spinner: {
    border: '4px solid #f3f3f3',
    borderTop: '4px solid #667eea',
    borderRadius: '50%',
    width: '50px',
    height: '50px',
    animation: 'spin 1s linear infinite',
    margin: '0 auto 20px',
  },
  loadingText: {
    color: '#1976D2',
    fontSize: '18px',
    marginBottom: '10px',
  },
  loadingSubtext: {
    color: '#666',
    fontSize: '14px',
    margin: 0,
  },
  error: {
    background: '#f8d7da',
    color: '#721c24',
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '20px',
    border: '1px solid #f5c6cb',
  },
  result: {
    padding: '25px',
    borderRadius: '10px',
    border: '2px solid',
    marginTop: '20px',
  },
  resultTitle: {
    margin: '0 0 10px 0',
    fontSize: '24px',
  },
  resultText: {
    margin: '10px 0',
    fontSize: '16px',
  },
  confidence: {
    margin: '15px 0 10px 0',
    fontSize: '16px',
  },
  progressBar: {
    width: '100%',
    height: '20px',
    background: '#e9ecef',
    borderRadius: '10px',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    transition: 'width 0.3s ease',
  }
};

// Add CSS animation for spinner
const styleSheet = document.createElement("style");
styleSheet.textContent = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;
document.head.appendChild(styleSheet);

export default FaceVerification;