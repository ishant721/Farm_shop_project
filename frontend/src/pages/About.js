import React from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';

const AboutContainer = styled.div`
  padding-top: 120px;
  min-height: 100vh;
`;

const HeroSection = styled.section`
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.1), rgba(32, 201, 151, 0.1));
  padding: 80px 0;
  text-align: center;
`;

const AboutTitle = styled(motion.h1)`
  font-size: clamp(2.5rem, 5vw, 3.5rem);
  margin-bottom: 2rem;
  background: linear-gradient(135deg, #28a745, #20c997);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const AboutSubtitle = styled(motion.p)`
  font-size: 1.3rem;
  max-width: 800px;
  margin: 0 auto;
  color: #666;
  line-height: 1.8;
`;

const StorySection = styled.section`
  padding: 100px 0;
  background: white;
`;

const StoryGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
`;

const StoryImage = styled(motion.div)`
  background: linear-gradient(135deg, #28a745, #20c997);
  height: 400px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 8rem;
  color: white;
`;

const StoryContent = styled(motion.div)`
  h2 {
    font-size: 2.5rem;
    margin-bottom: 1.5rem;
    color: #333;
  }

  p {
    font-size: 1.1rem;
    line-height: 1.8;
    color: #666;
    margin-bottom: 1.5rem;
  }
`;

const About = () => {
  return (
    <AboutContainer>
      <HeroSection>
        <div className="container">
          <AboutTitle
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            About R.S. Krishi Seva Kendra
          </AboutTitle>
          <AboutSubtitle
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Leading farm equipment dealer serving farmers since 1995
          </AboutSubtitle>
        </div>
      </HeroSection>

      <StorySection>
        <StoryGrid>
          <StoryImage
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            🌾
          </StoryImage>
          <StoryContent
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2>Our Story</h2>
            <p>
              Founded by Ramesh Singh, a passionate advocate for sustainable agriculture, 
              R.S. Krishi Seva Kendra began as a small local initiative to help farmers 
              get fair prices for their produce while providing consumers with access to 
              fresh, chemical-free food.
            </p>
            <p>
              Today, we work with over 200 local farmers across the region, ensuring 
              sustainable farming practices while building a community that values 
              quality, freshness, and environmental responsibility.
            </p>
          </StoryContent>
        </StoryGrid>
      </StorySection>
    </AboutContainer>
  );
};

export default About;