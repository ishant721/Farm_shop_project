
import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const HomeContainer = styled.div`
  padding-top: 80px;
  min-height: 100vh;
`;

const HeroSection = styled(motion.section)`
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.9), rgba(32, 201, 151, 0.9)),
              url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="%23ffffff" opacity="0.1"/></pattern></defs><rect width="100%" height="100%" fill="url(%23grain)"/></svg>');
  color: white;
  text-align: center;
  padding: 100px 0;
  position: relative;
  overflow: hidden;
`;

const HeroContent = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 0 2rem;
`;

const HeroTitle = styled(motion.h1)`
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 700;
  margin-bottom: 1.5rem;
  line-height: 1.2;
`;

const HeroSubtitle = styled(motion.p)`
  font-size: clamp(1.1rem, 2vw, 1.3rem);
  margin-bottom: 2rem;
  opacity: 0.95;
`;

const HeroButtons = styled(motion.div)`
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
`;

const FeaturesSection = styled.section`
  padding: 100px 0;
  background: white;
`;

const SectionTitle = styled(motion.h2)`
  text-align: center;
  font-size: clamp(2rem, 4vw, 3rem);
  margin-bottom: 3rem;
  background: linear-gradient(135deg, #28a745, #20c997);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const FeatureGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
`;

const FeatureCard = styled(motion.div)`
  background: white;
  padding: 2rem;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  }
`;

const FeatureIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #28a745, #20c997);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const AnimatedBackground = styled(motion.div)`
  position: absolute;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  top: ${props => props.top}%;
  left: ${props => props.left}%;
`;

const Home = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.6 }
    }
  };

  return (
    <HomeContainer>
      <HeroSection
        initial="hidden"
        animate="visible"
        variants={containerVariants}
      >
        <AnimatedBackground
          top={10}
          left={10}
          animate={{
            y: [0, -20, 0],
            scale: [1, 1.1, 1]
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            repeatType: "reverse"
          }}
        />
        <AnimatedBackground
          top={60}
          left={80}
          animate={{
            y: [0, 20, 0],
            scale: [1, 0.9, 1]
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            repeatType: "reverse"
          }}
        />
        
        <HeroContent>
          <HeroTitle variants={itemVariants}>
            Welcome to R.S. Krishi Seva Kendra
          </HeroTitle>
          <HeroSubtitle variants={itemVariants}>
            Your trusted partner for fresh, organic, and locally sourced agricultural products. 
            Supporting farmers and serving communities with quality produce.
          </HeroSubtitle>
          <HeroButtons variants={itemVariants}>
            <Link to="/products" className="btn btn-primary">
              Explore Products
            </Link>
            <Link to="/register" className="btn btn-outline">
              Join Our Community
            </Link>
          </HeroButtons>
        </HeroContent>
      </HeroSection>

      <FeaturesSection>
        <div className="container">
          <SectionTitle
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            Why Choose R.S. Krishi Seva Kendra?
          </SectionTitle>
          
          <FeatureGrid>
            <FeatureCard
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.05 }}
            >
              <FeatureIcon>🌱</FeatureIcon>
              <h3>Fresh & Organic</h3>
              <p>Direct from farm to your table. All our products are certified organic and freshly harvested.</p>
              <Link to="/products" className="btn btn-outline" style={{ marginTop: '1rem' }}>
                Shop Fresh Produce
              </Link>
            </FeatureCard>

            <FeatureCard
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.05 }}
            >
              <FeatureIcon>👨‍🌾</FeatureIcon>
              <h3>Support Local Farmers</h3>
              <p>Every purchase directly supports local farmers and helps build sustainable agricultural communities.</p>
              <Link to="/about" className="btn btn-outline" style={{ marginTop: '1rem' }}>
                Learn More
              </Link>
            </FeatureCard>

            <FeatureCard
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.05 }}
            >
              <FeatureIcon>🏢</FeatureIcon>
              <h3>Business Solutions</h3>
              <p>Bulk orders, competitive pricing, and reliable supply chains for restaurants and retailers.</p>
              <Link to="/services" className="btn btn-outline" style={{ marginTop: '1rem' }}>
                Business Services
              </Link>
            </FeatureCard>
          </FeatureGrid>
        </div>
      </FeaturesSection>
    </HomeContainer>
  );
};

export default Home;
