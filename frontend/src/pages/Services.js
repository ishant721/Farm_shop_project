import React from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';

const ServicesContainer = styled.div`
  padding-top: 120px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
`;

const ServicesTitle = styled(motion.h1)`
  text-align: center;
  font-size: clamp(2.5rem, 5vw, 3.5rem);
  margin-bottom: 3rem;
  background: linear-gradient(135deg, #28a745, #20c997);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const ServicesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
`;

const ServiceCard = styled(motion.div)`
  background: white;
  padding: 2.5rem;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
    background: linear-gradient(135deg, #28a745, #20c997);
  }
`;

const ServiceIcon = styled.div`
  font-size: 4rem;
  margin-bottom: 1.5rem;
`;

const ServiceTitle = styled.h3`
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #333;
`;

const ServiceDescription = styled.p`
  color: #666;
  line-height: 1.6;
  margin-bottom: 1.5rem;
`;

const Services = () => {
  const services = [
    {
      icon: "🛒",
      title: "Retail Shopping",
      description: "Browse and purchase fresh produce, grains, and organic products directly from our store or online platform."
    },
    {
      icon: "🏢",
      title: "Bulk Orders",
      description: "Special pricing and dedicated support for restaurants, hotels, and retail businesses requiring large quantities."
    },
    {
      icon: "🚚",
      title: "Home Delivery",
      description: "Fast and reliable delivery service to bring fresh products directly to your doorstep."
    },
    {
      icon: "👨‍🌾",
      title: "Farmer Support",
      description: "Training, resources, and market access for local farmers to improve their yield and income."
    },
    {
      icon: "🌱",
      title: "Organic Certification",
      description: "Assistance with organic certification process and maintaining sustainable farming practices."
    },
    {
      icon: "📊",
      title: "Market Analytics",
      description: "Data-driven insights on crop prices, demand trends, and optimal planting schedules."
    }
  ];

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
    hidden: { y: 50, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.6 }
    }
  };

  return (
    <ServicesContainer>
      <div className="container">
        <ServicesTitle
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          Our Services
        </ServicesTitle>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <ServicesGrid>
            {services.map((service, index) => (
              <ServiceCard
                key={index}
                variants={itemVariants}
                whileHover={{ 
                  scale: 1.05,
                  boxShadow: "0 20px 40px rgba(0, 0, 0, 0.15)"
                }}
                whileTap={{ scale: 0.98 }}
              >
                <ServiceIcon>{service.icon}</ServiceIcon>
                <ServiceTitle>{service.title}</ServiceTitle>
                <ServiceDescription>{service.description}</ServiceDescription>
                <motion.button
                  className="btn btn-outline"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Learn More
                </motion.button>
              </ServiceCard>
            ))}
              <ServiceCard
                variants={itemVariants}
                whileHover={{ 
                  scale: 1.05,
                  boxShadow: "0 20px 40px rgba(0, 0, 0, 0.15)"
                }}
                whileTap={{ scale: 0.98 }}
              >
                <ServiceIcon>💰</ServiceIcon>
                <h3>Government Subsidy Support</h3>
                <p>Authorized dealer for MP Government subsidy schemes. Get up to 50% subsidy on eligible farm implements through government programs.</p>
              </ServiceCard>

              <ServiceCard
                variants={itemVariants}
                whileHover={{ 
                  scale: 1.05,
                  boxShadow: "0 20px 40px rgba(0, 0, 0, 0.15)"
                }}
                whileTap={{ scale: 0.98 }}
              >
                <ServiceIcon>📋</ServiceIcon>
                <h3>Subsidy Documentation</h3>
                <p>Complete assistance with subsidy paperwork and government formalities. We handle all documentation to ensure you get maximum benefits.</p>
              </ServiceCard>
          </ServicesGrid>
        </motion.div>
      </div>
    </ServicesContainer>
  );
};

export default Services;