
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';

const ProductsContainer = styled.div`
  padding-top: 120px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
`;

const ProductsHeader = styled.div`
  text-align: center;
  margin-bottom: 3rem;
  padding: 0 2rem;
`;

const ProductsTitle = styled(motion.h1)`
  font-size: clamp(2.5rem, 5vw, 3.5rem);
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #28a745, #20c997);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const SearchBar = styled(motion.div)`
  max-width: 500px;
  margin: 0 auto 2rem;
  position: relative;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 15px 20px;
  border: none;
  border-radius: 50px;
  font-size: 1rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  outline: none;
  transition: all 0.3s ease;

  &:focus {
    box-shadow: 0 10px 30px rgba(40, 167, 69, 0.3);
  }
`;

const ProductGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
`;

const ProductCard = styled(motion.div)`
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  }
`;

const ProductImage = styled.div`
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, #28a745, #20c997);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  color: white;
`;

const ProductInfo = styled.div`
  padding: 1.5rem;
`;

const ProductName = styled.h3`
  font-size: 1.3rem;
  margin-bottom: 0.5rem;
  color: #333;
`;

const ProductDescription = styled.p`
  color: #666;
  margin-bottom: 1rem;
  line-height: 1.5;
`;

const ProductPrice = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
  color: #28a745;
  margin-bottom: 1rem;
`;

const ProductButton = styled(motion.button)`
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
  }
`;

const LoadingSpinner = styled(motion.div)`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 2rem;
`;

const Products = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data - replace with actual API call
  useEffect(() => {
    setTimeout(() => {
      setProducts([
        {
          id: 1,
          name: "Fresh Organic Tomatoes",
          description: "Locally grown, pesticide-free tomatoes perfect for your kitchen.",
          price: 45.00,
          emoji: "🍅"
        },
        {
          id: 2,
          name: "Premium Basmati Rice",
          description: "Aromatic long-grain rice, perfect for biryanis and pulao.",
          price: 120.00,
          emoji: "🍚"
        },
        {
          id: 3,
          name: "Fresh Green Vegetables",
          description: "Mixed seasonal vegetables, fresh from our partner farms.",
          price: 85.00,
          emoji: "🥬"
        },
        {
          id: 4,
          name: "Organic Wheat Flour",
          description: "Stone-ground wheat flour, rich in nutrients and flavor.",
          price: 55.00,
          emoji: "🌾"
        },
        {
          id: 5,
          name: "Farm Fresh Eggs",
          description: "Free-range eggs from healthy, happy chickens.",
          price: 25.00,
          emoji: "🥚"
        },
        {
          id: 6,
          name: "Pure Honey",
          description: "Raw, unprocessed honey directly from local beekeepers.",
          price: 180.00,
          emoji: "🍯"
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.5 }
    }
  };

  return (
    <ProductsContainer>
      <div className="container">
        <ProductsHeader>
          <ProductsTitle
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            Our Fresh Products
          </ProductsTitle>
          
          <SearchBar
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <SearchInput
              type="text"
              placeholder="Search for products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </SearchBar>
        </ProductsHeader>

        {loading ? (
          <LoadingSpinner
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            🌱
          </LoadingSpinner>
        ) : (
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <ProductGrid>
              {filteredProducts.map((product, index) => (
                <ProductCard
                  key={product.id}
                  variants={itemVariants}
                  whileHover={{ scale: 1.05 }}
                  layout
                >
                  <ProductImage>
                    {product.emoji}
                  </ProductImage>
                  <ProductInfo>
                    <ProductName>{product.name}</ProductName>
                    <ProductDescription>{product.description}</ProductDescription>
                    <ProductPrice>₹{product.price.toFixed(2)}</ProductPrice>
                    <ProductButton
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      Add to Cart
                    </ProductButton>
                  </ProductInfo>
                </ProductCard>
              ))}
            </ProductGrid>
          </motion.div>
        )}
      </div>
    </ProductsContainer>
  );
};

export default Products;
