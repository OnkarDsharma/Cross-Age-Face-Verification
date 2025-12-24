import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth APIs
export const signup = async (email, username, password) => {
  const response = await api.post('/auth/signup', {
    email,
    username,
    password,
  });
  return response.data;
};

export const login = async (username, password) => {
  const response = await api.post('/auth/login', {
    username,
    password,
  });
  
  // Store token
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
  }
  
  return response.data;
};

export const getCurrentUser = async () => {
  const token = localStorage.getItem('token');
  
  if (!token) {
    throw new Error('No token found');
  }
  
  const response = await api.get('/auth/me', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('token');
};

// Verification APIs
export const verifyFaces = async (image1, image2) => {
  const formData = new FormData();
  formData.append('image1', image1);
  formData.append('image2', image2);

  const response = await api.post('/verify/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getVerificationHistory = async () => {
  const response = await api.get('/verify/history');
  return response.data;
};

export default api;