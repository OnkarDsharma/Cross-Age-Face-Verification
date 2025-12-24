import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Signup from './components/Signup';
import FaceVerification from './components/FaceVerification';
import History from './components/History';
import { getCurrentUser, logout } from './services/api';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showLogin, setShowLogin] = useState(true);
  const [loading, setLoading] = useState(true);
  const [currentView, setCurrentView] = useState('verify');
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        logout();
        setIsAuthenticated(false);
      }
    }
    setLoading(false);
  };

  const handleLoginSuccess = async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Failed to get user data:', error);
    }
  };

  const handleSignupSuccess = () => {
    setShowLogin(true);
    alert('Account created successfully! Please login.');
  };

  const handleLogout = () => {
    logout();
    setIsAuthenticated(false);
    setUser(null);
  };

  if (loading) {
    return (
      <div style={styles.loading}>
        <div style={styles.spinner}></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return showLogin ? (
      <Login
        onLoginSuccess={handleLoginSuccess}
        onSwitchToSignup={() => setShowLogin(false)}
      />
    ) : (
      <Signup
        onSignupSuccess={handleSignupSuccess}
        onSwitchToLogin={() => setShowLogin(true)}
      />
    );
  }

  return (
    <div style={styles.app}>
      <nav style={styles.navbar}>
        <div style={styles.navBrand}>
          <h1 style={styles.brandTitle}>🔍 Face Verification</h1>
        </div>
        <div style={styles.navMenu}>
          <button
            onClick={() => setCurrentView('verify')}
            style={{
              ...styles.navBtn,
              ...(currentView === 'verify' ? styles.navBtnActive : {})
            }}
          >
            Verify
          </button>
          <button
            onClick={() => setCurrentView('history')}
            style={{
              ...styles.navBtn,
              ...(currentView === 'history' ? styles.navBtnActive : {})
            }}
          >
            History
          </button>
        </div>
        <div style={styles.navUser}>
          <span style={styles.username}>👤 {user?.username}</span>
          <button onClick={handleLogout} style={styles.logoutBtn}>
            Logout
          </button>
        </div>
      </nav>

      <main style={styles.main}>
        {currentView === 'verify' ? <FaceVerification /> : <History />}
      </main>

      <footer style={styles.footer}>
        <p>Cross-Age Face Verification System © 2025</p>
      </footer>
    </div>
  );
}

const styles = {
  app: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    background: '#f5f5f5',
  },
  loading: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
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
  navbar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '15px 30px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
  },
  navBrand: {
    flex: 1,
  },
  brandTitle: {
    margin: 0,
    fontSize: '24px',
  },
  navMenu: {
    display: 'flex',
    gap: '10px',
    flex: 1,
    justifyContent: 'center',
  },
  navBtn: {
    padding: '10px 25px',
    background: 'rgba(255,255,255,0.2)',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '500',
    transition: 'all 0.3s',
  },
  navBtnActive: {
    background: 'white',
    color: '#667eea',
  },
  navUser: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    flex: 1,
    justifyContent: 'flex-end',
  },
  username: {
    fontSize: '14px',
  },
  logoutBtn: {
    padding: '10px 20px',
    background: 'white',
    color: '#667eea',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontWeight: '600',
  },
  main: {
    flex: 1,
    padding: '20px',
  },
  footer: {
    textAlign: 'center',
    padding: '20px',
    background: '#333',
    color: 'white',
    marginTop: 'auto',
  }
};

export default App;