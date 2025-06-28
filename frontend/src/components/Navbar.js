
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import styled from 'styled-components';

const NavbarContainer = styled(motion.nav)`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 1rem 0;
  position: fixed;
  top: 0;
  width: 100%;
  z-index: 1000;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
`;

const NavContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;

  @media (max-width: 768px) {
    padding: 0 1rem;
  }
`;

const Logo = styled(motion.div)`
  font-size: 1.8rem;
  font-weight: bold;
  background: linear-gradient(135deg, #28a745, #20c997);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const NavLinks = styled.div`
  display: flex;
  gap: 2rem;
  align-items: center;

  @media (max-width: 768px) {
    display: ${props => props.isOpen ? 'flex' : 'none'};
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    background: white;
    flex-direction: column;
    padding: 2rem;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  }
`;

const NavLink = styled(motion(Link))`
  text-decoration: none;
  color: #333;
  font-weight: 500;
  position: relative;
  
  &:hover {
    color: #28a745;
  }

  &::after {
    content: '';
    position: absolute;
    width: 0;
    height: 2px;
    bottom: -5px;
    left: 0;
    background: linear-gradient(135deg, #28a745, #20c997);
    transition: width 0.3s ease;
  }

  &:hover::after {
    width: 100%;
  }
`;

const MobileToggle = styled.button`
  display: none;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;

  @media (max-width: 768px) {
    display: block;
  }
`;

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <NavbarContainer
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      style={{
        background: scrolled 
          ? 'rgba(255, 255, 255, 0.98)' 
          : 'rgba(255, 255, 255, 0.95)'
      }}
    >
      <NavContent>
        <Logo
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          R.S. Krishi Seva Kendra
        </Logo>
        
        <NavLinks isOpen={isOpen}>
          <NavLink 
            to="/" 
            whileHover={{ y: -2 }}
            onClick={() => setIsOpen(false)}
          >
            Home
          </NavLink>
          <NavLink 
            to="/products" 
            whileHover={{ y: -2 }}
            onClick={() => setIsOpen(false)}
          >
            Products
          </NavLink>
          <NavLink 
            to="/about" 
            whileHover={{ y: -2 }}
            onClick={() => setIsOpen(false)}
          >
            About Us
          </NavLink>
          <NavLink 
            to="/services" 
            whileHover={{ y: -2 }}
            onClick={() => setIsOpen(false)}
          >
            Services
          </NavLink>
          <NavLink 
            to="/contact" 
            whileHover={{ y: -2 }}
            onClick={() => setIsOpen(false)}
          >
            Contact
          </NavLink>
          <NavLink 
            to="/login" 
            whileHover={{ y: -2 }}
            onClick={() => setIsOpen(false)}
          >
            Login
          </NavLink>
        </NavLinks>

        <MobileToggle onClick={() => setIsOpen(!isOpen)}>
          ☰
        </MobileToggle>
      </NavContent>
    </NavbarContainer>
  );
};

export default Navbar;
