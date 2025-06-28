import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Add auth token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle responses and errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Authentication - using Django URLs
  login: (credentials) => api.post('/users/login/', credentials),
  register: (userData) => api.post('/users/register/', userData),
  logout: () => {
    localStorage.removeItem('authToken');
    return api.post('/users/logout/');
  },

  // Products
  getProducts: () => api.get('/api/products/'),
  getProduct: (id) => api.get(`/api/products/${id}/`),

  // Contact
  sendMessage: (messageData) => api.post('/api/contact/', messageData),

  // Cart
  getCart: () => api.get('/api/cart/'),
  addToCart: (productId, quantity) => api.post('/api/cart/add/', { product_id: productId, quantity }),
  updateCart: (itemId, quantity) => api.patch(`/api/cart/items/${itemId}/`, { quantity }),
  removeFromCart: (itemId) => api.delete(`/api/cart/items/${itemId}/`),
};

export default api;