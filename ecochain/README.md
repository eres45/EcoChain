# 🌱 EcoChain Guardian

EcoChain Guardian is an agent-based system that monitors crypto mining operations globally, scores them based on their carbon footprint using AI/ML techniques, and rewards eco-friendly miners with cryptocurrency tokens.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Development](#development)
- [License](#license)

## Overview

The environmental impact of cryptocurrency mining is significant and growing. EcoChain Guardian aims to incentivize more sustainable mining practices by:

1. **Monitoring** mining operations worldwide
2. **Analyzing** their environmental impact using AI/ML
3. **Scoring** them on sustainability metrics
4. **Rewarding** eco-friendly miners with ERC-20 tokens and NFT badges

By creating financial incentives for sustainable practices, EcoChain Guardian helps drive the crypto industry toward environmental responsibility.

## Key Features

- **Data Collection**: Gather mining operation data and carbon footprint information from various sources
- **AI/ML Analysis**: Score mining operations based on multiple sustainability factors
- **Smart Contract Rewards**: Issue ERC-20 tokens and NFT badges to eco-friendly miners
- **Tiered Reward System**: Higher sustainability scores earn greater rewards
- **Improvement Suggestions**: Provide miners with actionable suggestions for improving their sustainability
- **Transparent Reporting**: Track performance and impact over time

## Architecture

EcoChain Guardian follows a modular architecture based on the Superior Agents framework:

### Data Module
Collects and processes data from mining operations, including:
- Mining hardware information
- Energy consumption metrics
- Carbon footprint data
- Energy source information

### Analysis Module
Processes mining data to evaluate sustainability:
- ML-based scoring model
- Multi-factor sustainability assessment
- Tiered classification system
- Improvement recommendations

### Reward Module
Handles the distribution of incentives:
- ERC-20 token minting and distribution
- NFT badges for sustainability achievements
- Smart contract interactions
- Balance tracking

### Agent Module
Coordinates all activities:
- Workflow orchestration
- Scheduling of analysis and reward cycles
- Reporting and data storage
- Error handling and recovery

## Installation

### Prerequisites

- Python 3.8 or higher
- Web3 provider (for blockchain interactions)
- Git

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/your-username/EcoChainGuardian.git
cd EcoChainGuardian
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

## Configuration

1. Generate a default configuration:
```bash
ecochain setup
```

This creates a configuration file at `config/ecochain.json` with default settings.

2. Edit the configuration file to customize:
- Analysis interval
- Reward distribution interval
- Web3 provider settings
- Reward parameters

## Usage

### Running the Agent

Start the EcoChain Guardian agent:
```bash
ecochain run
```

Run a single analysis and reward cycle:
```bash
ecochain run --once
```

### Data Collection

Collect and view mining operation data:
```bash
ecochain collect
```

### Analysis

Run sustainability analysis on mining operations:
```bash
ecochain analyze
```

### Reward Simulation

Simulate the reward distribution process:
```bash
ecochain simulate
```

## API Reference

The EcoChain Guardian system provides several programmatic interfaces:

### DataCollector

```python
from ecochain.data_module.data_collector import DataCollector

collector = DataCollector()
operations = collector.get_mining_operations()
carbon_data = collector.get_carbon_data("operation-id")
energy_mix = collector.get_energy_mix_data("location")
```

### SustainabilityScorer

```python
from ecochain.analysis_module.sustainability_scorer import SustainabilityScorer

scorer = SustainabilityScorer()
score = scorer.score_operation(mining_data, carbon_data)
```

### EcoToken

```python
from ecochain.reward_module.eco_token import EcoToken

token = EcoToken()
token.update_miner_score(miner_address, score)
token.mint_reward(miner_address, score)
token.award_badge(miner_address, tier)
```

### EcoAgent

```python
from ecochain.agent_module.eco_agent import EcoAgent

agent = EcoAgent("path/to/config.json")
agent.run()
scores = agent.get_top_performers(limit=10)
```

## Development

### Project Structure

```
ecochain/
├── agent_module/        # Main agent orchestration
├── analysis_module/     # Sustainability scoring and ML models
├── data_module/         # Data collection and processing
├── reward_module/       # Token and NFT reward mechanisms
├── cli.py               # Command-line interface
└── README.md            # This file
```

### Adding New Data Sources

To add a new data source, extend the DataCollector class in `data_module/data_collector.py` with your new data collection methods.

### Modifying the Scoring Algorithm

The sustainability scoring algorithm is defined in `analysis_module/sustainability_scorer.py`. You can adjust the weights and factors to emphasize different sustainability aspects.

### Customizing Rewards

Reward distribution logic is in `reward_module/eco_token.py`. You can modify the token emission rate, reward formulas, and badge criteria.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details. 