
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      const response = await apiService.login(formData);
      
      // Store token if returned
      if (response.data.token) {
        localStorage.setItem('authToken', response.data.token);
      }
      
      // Redirect to dashboard or home
      navigate('/');
    } catch (error) {
      console.error('Login error:', error);
      setError(error.response?.data?.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4 }
    }
  };

  return (
    <div style={{
      paddingTop: '120px',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <motion.div
        style={{
          background: 'white',
          padding: '3rem',
          borderRadius: '20px',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
          width: '100%',
          maxWidth: '400px',
          margin: '0 1rem'
        }}
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <h1 style={{
          textAlign: 'center',
          marginBottom: '2rem',
          background: 'linear-gradient(135deg, #28a745, #20c997)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          Welcome Back to R.S. Krishi Seva Kendra
        </h1>
        
        {error && (
          <div style={{
            color: '#dc3545',
            background: '#f8d7da',
            border: '1px solid #f5c6cb',
            borderRadius: '5px',
            padding: '10px',
            marginBottom: '1rem',
            textAlign: 'center'
          }}>
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <motion.div style={{ marginBottom: '1.5rem' }} variants={itemVariants}>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontWeight: '600',
              color: '#333'
            }}>
              Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              style={{
                width: '100%',
                padding: '12px 15px',
                border: '2px solid #e9ecef',
                borderRadius: '10px',
                fontSize: '1rem',
                transition: 'all 0.3s ease',
                boxSizing: 'border-box'
              }}
              required
            />
          </motion.div>

          <motion.div style={{ marginBottom: '1.5rem' }} variants={itemVariants}>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontWeight: '600',
              color: '#333'
            }}>
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              style={{
                width: '100%',
                padding: '12px 15px',
                border: '2px solid #e9ecef',
                borderRadius: '10px',
                fontSize: '1rem',
                transition: 'all 0.3s ease',
                boxSizing: 'border-box'
              }}
              required
            />
          </motion.div>

          <motion.button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              marginBottom: '1rem',
              background: 'linear-gradient(135deg, #28a745, #20c997)',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '10px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              opacity: isLoading ? 0.7 : 1
            }}
            whileHover={!isLoading ? { scale: 1.02 } : {}}
            whileTap={!isLoading ? { scale: 0.98 } : {}}
            variants={itemVariants}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </motion.button>
        </form>

        <motion.div
          style={{ textAlign: 'center' }}
          variants={itemVariants}
        >
          <p style={{ margin: '0.5rem 0' }}>
            <Link to="/forgot-password" style={{ color: '#28a745', textDecoration: 'none' }}>
              Forgot Password?
            </Link>
          </p>
          <p style={{ margin: '0' }}>
            Don't have an account? <Link to="/register" style={{ color: '#28a745', textDecoration: 'none' }}>Register here</Link>
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Login;
