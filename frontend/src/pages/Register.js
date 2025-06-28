
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

const Register = () => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    userType: 'farmer'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
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
    setSuccess('');
    
    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }
    
    try {
      const userData = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        password: formData.password,
        user_type: formData.userType
      };
      
      const response = await apiService.register(userData);
      
      setSuccess('Registration successful! Please check your email for verification.');
      
      // Redirect to login after a delay
      setTimeout(() => {
        navigate('/login');
      }, 2000);
      
    } catch (error) {
      console.error('Registration error:', error);
      setError(error.response?.data?.message || 'Registration failed. Please try again.');
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
      background: 'linear-gradient(135deg, #20c997 0%, #28a745 100%)',
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
          maxWidth: '500px',
          margin: '2rem 1rem'
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
          Join R.S. Krishi Seva Kendra
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
        
        {success && (
          <div style={{
            color: '#155724',
            background: '#d4edda',
            border: '1px solid #c3e6cb',
            borderRadius: '5px',
            padding: '10px',
            marginBottom: '1rem',
            textAlign: 'center'
          }}>
            {success}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <motion.div style={{ marginBottom: '1.5rem' }} variants={itemVariants}>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                fontWeight: '600',
                color: '#333'
              }}>
                First Name
              </label>
              <input
                type="text"
                name="firstName"
                value={formData.firstName}
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
                Last Name
              </label>
              <input
                type="text"
                name="lastName"
                value={formData.lastName}
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
          </div>

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
              I am a
            </label>
            <select
              name="userType"
              value={formData.userType}
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
            >
              <option value="farmer">Farmer</option>
              <option value="business">Business Owner</option>
              <option value="customer">Customer</option>
            </select>
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

          <motion.div style={{ marginBottom: '1.5rem' }} variants={itemVariants}>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontWeight: '600',
              color: '#333'
            }}>
              Confirm Password
            </label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
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
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </motion.button>
        </form>

        <motion.div
          style={{ textAlign: 'center' }}
          variants={itemVariants}
        >
          <p style={{ margin: '0' }}>
            Already have an account? <Link to="/login" style={{ color: '#28a745', textDecoration: 'none' }}>Login here</Link>
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Register;
