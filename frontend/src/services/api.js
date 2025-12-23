const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const getToken = () => localStorage.getItem('token');
const setToken = (token) => localStorage.setItem('token', token);
const removeToken = () => localStorage.removeItem('token');

export const api = {
  async signup(email, username, password) {
    try {
      const response = await fetch(`${API_URL}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, username, password })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Signup failed');
      }
      
      return data;
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  },

  async login(username, password) {
    try {
      // IMPORTANT: Send as form data, not JSON!
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        const errorMsg = data.detail || 'Login failed. Please check your credentials.';
        throw new Error(errorMsg);
      }
      
      setToken(data.access_token);
      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  async getCurrentUser() {
    const token = getToken();
    if (!token) {
      throw new Error('No token found. Please login again.');
    }

    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.status === 401) {
        removeToken();
        throw new Error('Session expired. Please login again.');
      }
      
      if (!response.ok) {
        throw new Error('Failed to get user info');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Get user error:', error);
      throw error;
    }
  },

  async verifyFaces(image1, image2) {
    const token = getToken();
    if (!token) {
      throw new Error('Not authenticated. Please login.');
    }

    try {
      const formData = new FormData();
      formData.append('image1', image1);
      formData.append('image2', image2);
      
      const response = await fetch(`${API_URL}/verify/`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Verification failed');
      }
      
      return data;
    } catch (error) {
      console.error('Verification error:', error);
      throw error;
    }
  },

  async getHistory() {
    const token = getToken();
    if (!token) {
      throw new Error('Not authenticated. Please login.');
    }

    try {
      const response = await fetch(`${API_URL}/verify/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error('Failed to get history');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Get history error:', error);
      throw error;
    }
  },

  isAuthenticated() {
    return !!getToken();
  },

  logout() {
    removeToken();
  }
};