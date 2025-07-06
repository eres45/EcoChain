# 🌱 EcoChain Guardian

EcoChain Guardian is a blockchain-based platform for monitoring, analyzing, and rewarding sustainable cryptocurrency mining operations.

<p align="center">
  <img src="Jul 7, 2025, 04_17_26 AM.png" alt="EcoChain Guardian Logo" width="200">
</p>

## 🌟 Overview

The environmental impact of cryptocurrency mining is significant and growing. EcoChain Guardian aims to incentivize more sustainable mining practices by:

1. **Monitoring** mining operations worldwide
2. **Analyzing** their environmental impact using AI/ML
3. **Scoring** them on sustainability metrics
4. **Rewarding** eco-friendly miners with ERC-20 tokens and NFT badges

By creating financial incentives for sustainable practices, EcoChain Guardian helps drive the crypto industry toward environmental responsibility.

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- Docker and Docker Compose

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ecochain-guardian.git
cd ecochain-guardian
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
pip install -e .
```

3. Install web demo dependencies:
```bash
cd web-demo
npm install
cd ..
```

### Running the Platform

#### Start the Web Demo

```bash
cd web-demo
node server.js
```
The web demo will be available at http://localhost:3010

#### Start the Core Services

```bash
# Start all services using Docker Compose
docker-compose up -d

# Or run individual components
python ecochain/cli.py run
```

## 🔍 Key Features

### Core Features

- **Sustainability Scoring**: Comprehensive scoring system that evaluates mining operations based on energy sources, efficiency, and environmental impact
- **Optimization Advisor**: AI-powered recommendations for hardware upgrades, energy efficiency improvements, and cooling optimizations
- **Predictive Analytics**: Advanced forecasting of energy usage, costs, and market correlations
- **Compliance Reporting**: Automated generation of ESG reports and regulatory compliance documentation
- **Smart Contract Automation**: Automated deployment of reward distribution contracts based on sustainability scores
- **Zero-Knowledge Verification**: Cryptographic proof of renewable energy usage without revealing sensitive operational data

### Advanced Features

- **ML-based Scoring**: Machine learning model for accurate sustainability scoring with anomaly detection
- **zkSNARK Verification**: Zero-knowledge proofs for verified carbon reporting
- **DeFi Integration**: EcoToken staking with tier-based rewards
- **Community Governance**: DAO-style governance for parameter adjustment
- **Multi-chain Support**: Connect to multiple blockchains beyond Ethereum
- **Data Provider Network**: Decentralized oracle network for verified carbon data

## 🧪 Testing the Platform

### Testing the Web Demo

1. Navigate to http://localhost:3010 in your browser
2. Explore the interactive dashboard showing sustainability scores, optimization recommendations, and predictive analytics
3. Test the smart contract automation feature by filling out the form in the "Test Smart Contract Automation" section
4. Try the Zero-Knowledge Verification demo to see how miners can prove sustainability without revealing sensitive data

### Testing the ML Models

```bash
# Test the sustainability scoring model
python -m ecochain.analysis_module.sustainability_scorer --test

# Test the predictive analytics model
python -m ecochain.analysis_module.predictive_analytics --test

# Test the optimization advisor
python -m ecochain.analysis_module.optimization_advisor --test

# Run all tests
pytest
```

### Testing Smart Contracts

```bash
# Test the reward distribution contract
python agent/scripts/test_auto_contract.py

# Test the governance contract
python -m ecochain.reward_module.eco_governance --test

# Test the staking contract
python -m ecochain.reward_module.eco_staking --test
```

## 📊 Project Structure

```
ecochain/
├── agent/                # Superior Agents framework implementation
├── config/               # Configuration files
├── data/                 # Data files and ML models
├── db/                   # Database files
├── ecochain/             # Core EcoChain Guardian modules
│   ├── agent_module/     # Main agent orchestration
│   ├── analysis_module/  # Sustainability scoring and ML models
│   ├── api/              # API endpoints (REST and GraphQL)
│   ├── blockchain/       # Blockchain integrations
│   ├── data_module/      # Data collection and processing
│   ├── oracles/          # Oracle network for data verification
│   ├── reward_module/    # Token and NFT reward mechanisms
│   └── scripts/          # Utility scripts
├── meta-swap-api/        # Multi-chain swap API
├── notification/         # Notification service
├── rag-api/              # Retrieval-augmented generation API
├── web-demo/             # Interactive web demonstration
└── README.md             # This file
```

## 🔧 Configuration

### Core Configuration

Edit `config/ecochain.json` to customize:
- Analysis interval
- Reward distribution interval
- Web3 provider settings
- Reward parameters

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Web3 Configuration
WEB3_PROVIDER_URI=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
PRIVATE_KEY=your_private_key_for_contract_deployment

# API Configuration
API_PORT=5000
GRAPHQL_PORT=5001

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecochain
DB_USER=postgres
DB_PASSWORD=postgres

# ML Model Configuration
MODEL_PATH=data/models/sustainability_model.pkl
```

## 🖥️ API Reference

### REST API

The platform provides a RESTful API for integration with other systems:

```
GET /api/sustainability-scores - Get sustainability scores for mining operations
GET /api/optimization-recommendations - Get optimization recommendations
GET /api/predictive-analytics - Get predictive analytics data
GET /api/compliance-reports - Get compliance reports
GET /api/auto-contracts - Get information about automated contracts
GET /api/zk-verifications - Get zero-knowledge verification data
```

### GraphQL API

For more complex data queries, use the GraphQL API at `/graphql`.

## 💪 Advantages of EcoChain Guardian

### Environmental Impact

- **Reduces Carbon Footprint**: Incentivizes miners to adopt renewable energy sources
- **Promotes Efficiency**: Encourages use of more energy-efficient mining hardware
- **Measurable Impact**: Tracks and reports on environmental improvements over time

### Technical Innovation

- **Blockchain + ML Integration**: Combines blockchain technology with machine learning for accurate scoring
- **Zero-Knowledge Proofs**: Uses advanced cryptography to maintain privacy while ensuring transparency
- **Smart Contract Automation**: Reduces friction in reward distribution through automation

### Business Value

- **Incentive Alignment**: Creates financial incentives for sustainable practices
- **Transparency**: Provides verifiable proof of sustainability claims
- **Regulatory Readiness**: Helps miners prepare for potential future regulations
- **Brand Value**: Enhances reputation for environmentally conscious mining operations

### Practical Implementation

- **End-to-End Solution**: Covers everything from data collection to reward distribution
- **Scalable Architecture**: Designed to handle thousands of mining operations
- **User-Friendly Interface**: Easy-to-use dashboard for miners and stakeholders

## 📜 License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please see CONTRIBUTING.md for details on how to contribute to this project. 