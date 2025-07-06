// EcoChain Guardian Demo Server
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3010;

// Middleware
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// API endpoints for demo features
app.get('/api/sustainability-scores', (req, res) => {
  // Mock data for sustainability scores
  const scores = {
    operations: [
      { id: 1, name: 'Mining Operation A', score: 87, energySource: 'Solar', location: 'Nevada, USA' },
      { id: 2, name: 'Mining Operation B', score: 92, energySource: 'Wind', location: 'Scotland, UK' },
      { id: 3, name: 'Mining Operation C', score: 65, energySource: 'Mixed', location: 'Alberta, Canada' },
      { id: 4, name: 'Mining Operation D', score: 78, energySource: 'Hydro', location: 'Norway' },
      { id: 5, name: 'Mining Operation E', score: 45, energySource: 'Coal', location: 'Inner Mongolia, China' }
    ]
  };
  res.json(scores);
});

app.get('/api/optimization-recommendations', (req, res) => {
  // Mock data for optimization recommendations
  const recommendations = {
    hardware: [
      { type: 'ASIC Upgrade', description: 'Upgrade to Bitmain Antminer S19 XP for 30% efficiency improvement', roi: '8 months' },
      { type: 'GPU Undervolting', description: 'Apply optimal undervolt settings to reduce power by 15%', roi: '1 month' }
    ],
    cooling: [
      { type: 'Immersion Cooling', description: 'Implement two-phase immersion cooling to reduce cooling costs by 40%', roi: '14 months' },
      { type: 'Airflow Optimization', description: 'Reconfigure server room airflow patterns for 10% cooling efficiency', roi: '3 months' }
    ],
    energy: [
      { type: 'Solar Integration', description: 'Install 500kW solar array with battery storage', roi: '36 months' },
      { type: 'Load Shifting', description: 'Shift 40% of mining operations to off-peak hours', roi: '5 months' }
    ]
  };
  res.json(recommendations);
});

app.get('/api/predictive-analytics', (req, res) => {
  // Mock data for predictive analytics
  const analytics = {
    energyUsageForecast: [
      { month: 'Jan', predicted: 450, actual: 460 },
      { month: 'Feb', predicted: 470, actual: 465 },
      { month: 'Mar', predicted: 490, actual: 495 },
      { month: 'Apr', predicted: 510, actual: 505 },
      { month: 'May', predicted: 540, actual: null },
      { month: 'Jun', predicted: 580, actual: null }
    ],
    marketCorrelation: [
      { factor: 'Bitcoin Price', correlation: 0.72 },
      { factor: 'Electricity Costs', correlation: -0.85 },
      { factor: 'Renewable Energy Mix', correlation: 0.63 },
      { factor: 'Carbon Credit Price', correlation: 0.41 }
    ]
  };
  res.json(analytics);
});

app.get('/api/compliance-reports', (req, res) => {
  // Mock data for compliance reports
  const reports = {
    esgReports: [
      { id: 'ESG-2023-Q1', title: 'Q1 2023 ESG Report', score: 82, status: 'Verified', date: '2023-04-15' },
      { id: 'ESG-2023-Q2', title: 'Q2 2023 ESG Report', score: 86, status: 'Verified', date: '2023-07-15' },
      { id: 'ESG-2023-Q3', title: 'Q3 2023 ESG Report', score: 89, status: 'Verified', date: '2023-10-15' },
      { id: 'ESG-2023-Q4', title: 'Q4 2023 ESG Report', score: 91, status: 'Verified', date: '2024-01-15' }
    ],
    regulatoryCompliance: [
      { regulation: 'EU Sustainable Finance Disclosure', status: 'Compliant', lastAudit: '2024-02-10' },
      { regulation: 'SEC Climate Disclosure', status: 'Compliant', lastAudit: '2024-01-22' },
      { regulation: 'Carbon Border Adjustment Mechanism', status: 'In Progress', lastAudit: '2024-03-05' }
    ]
  };
  res.json(reports);
});

app.get('/api/auto-contracts', (req, res) => {
  // Mock data for auto contracts
  const contracts = {
    deployedContracts: [
      { id: 'ECR-001', name: 'EcoRewards Distribution', address: '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D', status: 'Active' },
      { id: 'EST-002', name: 'EcoStaking Pool', address: '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f', status: 'Active' },
      { id: 'EGV-003', name: 'EcoGovernance Voting', address: '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984', status: 'Pending' }
    ],
    rewardDistributions: [
      { date: '2024-01-15', amount: '125,000 ECO', recipients: 42, txHash: '0x8a6f...3e2d' },
      { date: '2024-02-15', amount: '130,000 ECO', recipients: 56, txHash: '0x7b5d...9f1c' },
      { date: '2024-03-15', amount: '128,000 ECO', recipients: 61, txHash: '0x6c4e...8d2b' }
    ]
  };
  res.json(contracts);
});

app.get('/api/zk-verifications', (req, res) => {
  // Mock data for ZK verifications
  const verifications = {
    verifiedProofs: [
      { id: 'ZKP-001', type: 'Renewable Energy Certificate', date: '2024-03-01', status: 'Verified' },
      { id: 'ZKP-002', type: 'Carbon Offset', date: '2024-03-05', status: 'Verified' },
      { id: 'ZKP-003', type: 'Energy Efficiency Improvement', date: '2024-03-10', status: 'Pending' }
    ]
  };
  res.json(verifications);
});

// Catch-all route to serve the main application
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start the server
app.listen(PORT, () => {
  console.log(`EcoChain Guardian Demo server running at http://localhost:${PORT}/`);
}); 