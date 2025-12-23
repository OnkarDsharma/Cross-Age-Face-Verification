import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await api.getHistory();
      setHistory(data);
    } catch (err) {
      setError(err.message || 'Failed to load history');
      console.error('History error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={styles.loading}>
        <div style={styles.spinner}></div>
        <p>Loading history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.error}>
        <strong>⚠ Error:</strong> {error}
        <button onClick={loadHistory} style={styles.retryBtn}>
          Retry
        </button>
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div style={styles.empty}>
        <div style={styles.emptyIcon}>📊</div>
        <h3>No verification history yet</h3>
        <p>Start verifying faces to see your history here!</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>Verification History</h2>
        <button onClick={loadHistory} style={styles.refreshBtn}>
          🔄 Refresh
        </button>
      </div>
      
      <div style={styles.stats}>
        <div style={styles.statCard}>
          <div style={styles.statNumber}>{history.length}</div>
          <div style={styles.statLabel}>Total Verifications</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statNumber}>
            {history.filter(h => h.result === 'match').length}
          </div>
          <div style={styles.statLabel}>Matches</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statNumber}>
            {history.filter(h => h.result === 'no_match').length}
          </div>
          <div style={styles.statLabel}>No Matches</div>
        </div>
      </div>

      <div style={styles.historyList}>
        {history.map((item) => (
          <div key={item.id} style={styles.historyItem}>
            <div style={styles.historyHeader}>
              <span style={{
                ...styles.badge,
                background: item.result === 'match' ? '#28a745' : '#dc3545'
              }}>
                {item.result === 'match' ? '✓ Match' : '✗ No Match'}
              </span>
              <span style={styles.date}>
                {new Date(item.created_at).toLocaleString()}
              </span>
            </div>
            <div style={styles.historyDetails}>
              <div style={styles.detailRow}>
                <strong>Confidence:</strong> {(item.confidence_score * 100).toFixed(2)}%
              </div>
              <div style={styles.confidenceBar}>
                <div style={{
                  ...styles.confidenceBarFill,
                  width: `${item.confidence_score * 100}%`,
                  background: item.result === 'match' ? '#28a745' : '#dc3545'
                }} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '30px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px',
  },
  title: {
    margin: 0,
    color: '#333',
    fontSize: '28px',
  },
  refreshBtn: {
    padding: '10px 20px',
    background: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
  },
  stats: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '20px',
    marginBottom: '30px',
  },
  statCard: {
    background: 'white',
    padding: '20px',
    borderRadius: '10px',
    textAlign: 'center',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  statNumber: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: '5px',
  },
  statLabel: {
    fontSize: '14px',
    color: '#666',
  },
  loading: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '400px',
    gap: '20px',
  },
  spinner: {
    border: '4px solid #f3f3f3',
    borderTop: '4px solid #667eea',
    borderRadius: '50%',
    width: '40px',
    height: '40px',
    animation: 'spin 1s linear infinite',
  },
  error: {
    background: '#f8d7da',
    color: '#721c24',
    padding: '20px',
    borderRadius: '8px',
    margin: '20px',
    textAlign: 'center',
    border: '1px solid #f5c6cb',
  },
  retryBtn: {
    marginTop: '15px',
    padding: '10px 20px',
    background: '#dc3545',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontWeight: '600',
  },
  empty: {
    textAlign: 'center',
    padding: '80px 20px',
    color: '#666',
  },
  emptyIcon: {
    fontSize: '64px',
    marginBottom: '20px',
  },
  historyList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },
  historyItem: {
    background: 'white',
    border: '1px solid #ddd',
    borderRadius: '8px',
    padding: '20px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  historyHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '15px',
  },
  badge: {
    padding: '6px 16px',
    borderRadius: '20px',
    color: 'white',
    fontWeight: '600',
    fontSize: '14px',
  },
  date: {
    color: '#666',
    fontSize: '14px',
  },
  historyDetails: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  detailRow: {
    fontSize: '14px',
    color: '#555',
  },
  confidenceBar: {
    width: '100%',
    height: '8px',
    background: '#e9ecef',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  confidenceBarFill: {
    height: '100%',
    transition: 'width 0.3s ease',
  }
};

export default History;
