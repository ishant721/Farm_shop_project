import React, { useState } from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';

const ContactContainer = styled.div`
  padding-top: 120px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
`;

const ContactGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
`;

const ContactInfo = styled(motion.div)`
  background: white;
  padding: 3rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
`;

const ContactForm = styled(motion.form)`
  background: white;
  padding: 3rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
`;

const FormGroup = styled(motion.div)`
  margin-bottom: 1.5rem;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: #28a745;
    box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1);
  }
`;

const Textarea = styled.textarea`
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-size: 1rem;
  resize: vertical;
  min-height: 120px;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: #28a745;
    box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1);
  }
`;

const ContactItem = styled(motion.div)`
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
  font-size: 1.1rem;
`;

const ContactIcon = styled.div`
  font-size: 2rem;
  margin-right: 1rem;
  background: linear-gradient(135deg, #28a745, #20c997);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    // Add form submission logic here
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 30, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.6 }
    }
  };

  return (
    <ContactContainer>
      <div className="container">
        <motion.h1
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          style={{
            textAlign: 'center',
            fontSize: 'clamp(2.5rem, 5vw, 3.5rem)',
            marginBottom: '3rem',
            background: 'linear-gradient(135deg, #28a745, #20c997)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}
        >
          Contact Us
        </motion.h1>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <ContactGrid>
            <ContactInfo variants={itemVariants}>
              <h2 style={{ marginBottom: '2rem', color: '#333' }}>Get in Touch</h2>

              <ContactItem variants={itemVariants}>
                <ContactIcon>📍</ContactIcon>
                <div>
                  <strong>Address:</strong><br />
                  Near Over Bridge, Beside Sunderson Colony<br />
                  Kechloha Mohalla, Maihar<br />
                  District Maihar, Madhya Pradesh
                </div>
              </ContactItem>

              <ContactItem variants={itemVariants}>
                <ContactIcon>📞</ContactIcon>
                <div>
                  <strong>Phone:</strong><br />
                  +91 93002 97974
                </div>
              </ContactItem>

              <ContactItem variants={itemVariants}>
                <ContactIcon>👤</ContactIcon>
                <div>
                  <strong>Proprietor:</strong><br />
                  Devendra Singh
                </div>
              </ContactItem>

              <ContactItem variants={itemVariants}>
                <ContactIcon>✉️</ContactIcon>
                <div>
                  <strong>Email:</strong><br />
                  info@rskrishisevakendra.com
                </div>
              </ContactItem>

              <ContactItem variants={itemVariants}>
                <ContactIcon>🕒</ContactIcon>
                <div>
                  <strong>Hours:</strong><br />
                  Mon-Sat: 8:00 AM - 7:00 PM<br />
                  Sunday: 9:00 AM - 5:00 PM
                </div>
              </ContactItem>
            </ContactInfo>

            <ContactForm variants={itemVariants} onSubmit={handleSubmit}>
              <h2 style={{ marginBottom: '2rem', color: '#333' }}>Send us a Message</h2>

              <FormGroup variants={itemVariants}>
                <Label htmlFor="name">Name</Label>
                <Input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
              </FormGroup>

              <FormGroup variants={itemVariants}>
                <Label htmlFor="email">Email</Label>
                <Input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </FormGroup>

              <FormGroup variants={itemVariants}>
                <Label htmlFor="message">Message</Label>
                <Textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  required
                />
              </FormGroup>

              <motion.button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%' }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                variants={itemVariants}
              >
                Send Message
              </motion.button>
            </ContactForm>
          </ContactGrid>
        </motion.div>
      </div>
    </ContactContainer>
  );
};

export default Contact;