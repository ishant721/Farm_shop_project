
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
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

export const apiService = {
  // Products
  getProducts: () => api.get('/products/'),
  getProduct: (id) => api.get(`/products/${id}/`),
  
  // Authentication
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  logout: () => api.post('/auth/logout/'),
  
  // Contact
  sendMessage: (messageData) => api.post('/contact/', messageData),
  
  // Cart
  getCart: () => api.get('/cart/'),
  addToCart: (productId, quantity) => api.post('/cart/add/', { product_id: productId, quantity }),
  updateCart: (itemId, quantity) => api.patch(`/cart/items/${itemId}/`, { quantity }),
  removeFromCart: (itemId) => api.delete(`/cart/items/${itemId}/`),
};

export default api;
