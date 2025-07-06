// EcoChain Guardian Demo - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Initialize all components
  initNavigation();
  loadSustainabilityScores();
  loadOptimizationRecommendations();
  loadPredictiveAnalytics();
  loadComplianceReports();
  loadAutoContracts();
  loadZkVerifications();
  setupTestFeatures();
  setupCharts();
});

// Navigation functionality
function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Remove active class from all links
      navLinks.forEach(l => l.classList.remove('active'));
      
      // Add active class to clicked link
      this.classList.add('active');
      
      // Scroll to section
      const targetId = this.getAttribute('href').substring(1);
      const targetSection = document.getElementById(targetId);
      
      if (targetSection) {
        window.scrollTo({
          top: targetSection.offsetTop - 80,
          behavior: 'smooth'
        });
      }
    });
  });
}

// Load sustainability scores from API
function loadSustainabilityScores() {
  fetch('/api/sustainability-scores')
    .then(response => response.json())
    .then(data => {
      const tableBody = document.getElementById('sustainability-scores-table');
      if (!tableBody) return;
      
      tableBody.innerHTML = '';
      
      data.operations.forEach(operation => {
        const row = document.createElement('tr');
        
        // Determine score class
        let scoreClass = 'badge-warning';
        if (operation.score >= 80) {
          scoreClass = 'badge-success';
        } else if (operation.score < 60) {
          scoreClass = 'badge-danger';
        }
        
        row.innerHTML = `
          <td>${operation.name}</td>
          <td>${operation.location}</td>
          <td>${operation.energySource}</td>
          <td><span class="badge ${scoreClass}">${operation.score}</span></td>
          <td>
            <button class="btn btn-sm btn-outline" onclick="viewOperationDetails(${operation.id})">View Details</button>
          </td>
        `;
        
        tableBody.appendChild(row);
      });
    })
    .catch(error => {
      console.error('Error loading sustainability scores:', error);
      showErrorMessage('sustainability-scores-container', 'Failed to load sustainability scores');
    });
}

// Load optimization recommendations from API
function loadOptimizationRecommendations() {
  fetch('/api/optimization-recommendations')
    .then(response => response.json())
    .then(data => {
      // Hardware recommendations
      const hardwareContainer = document.getElementById('hardware-recommendations');
      if (hardwareContainer) {
        hardwareContainer.innerHTML = '';
        data.hardware.forEach(rec => {
          const card = document.createElement('div');
          card.className = 'feature-card';
          card.innerHTML = `
            <h4>${rec.type}</h4>
            <p>${rec.description}</p>
            <p><strong>ROI:</strong> ${rec.roi}</p>
          `;
          hardwareContainer.appendChild(card);
        });
      }
      
      // Cooling recommendations
      const coolingContainer = document.getElementById('cooling-recommendations');
      if (coolingContainer) {
        coolingContainer.innerHTML = '';
        data.cooling.forEach(rec => {
          const card = document.createElement('div');
          card.className = 'feature-card';
          card.innerHTML = `
            <h4>${rec.type}</h4>
            <p>${rec.description}</p>
            <p><strong>ROI:</strong> ${rec.roi}</p>
          `;
          coolingContainer.appendChild(card);
        });
      }
      
      // Energy recommendations
      const energyContainer = document.getElementById('energy-recommendations');
      if (energyContainer) {
        energyContainer.innerHTML = '';
        data.energy.forEach(rec => {
          const card = document.createElement('div');
          card.className = 'feature-card';
          card.innerHTML = `
            <h4>${rec.type}</h4>
            <p>${rec.description}</p>
            <p><strong>ROI:</strong> ${rec.roi}</p>
          `;
          energyContainer.appendChild(card);
        });
      }
    })
    .catch(error => {
      console.error('Error loading optimization recommendations:', error);
      showErrorMessage('optimization-container', 'Failed to load optimization recommendations');
    });
}

// Load predictive analytics from API
function loadPredictiveAnalytics() {
  fetch('/api/predictive-analytics')
    .then(response => response.json())
    .then(data => {
      // Store data for charts
      window.analyticsData = data;
      
      // Update correlation table
      const correlationTable = document.getElementById('market-correlation-table');
      if (correlationTable) {
        correlationTable.innerHTML = '';
        
        data.marketCorrelation.forEach(item => {
          const row = document.createElement('tr');
          
          // Determine correlation class
          let correlationClass = '';
          if (item.correlation > 0.7) {
            correlationClass = 'text-success';
          } else if (item.correlation < 0) {
            correlationClass = 'text-danger';
          }
          
          row.innerHTML = `
            <td>${item.factor}</td>
            <td class="${correlationClass}">${item.correlation.toFixed(2)}</td>
          `;
          
          correlationTable.appendChild(row);
        });
      }
      
      // If charts are loaded, update them
      if (window.energyForecastChart) {
        updateEnergyForecastChart(data.energyUsageForecast);
      }
    })
    .catch(error => {
      console.error('Error loading predictive analytics:', error);
      showErrorMessage('predictive-analytics-container', 'Failed to load predictive analytics');
    });
}

// Load compliance reports from API
function loadComplianceReports() {
  fetch('/api/compliance-reports')
    .then(response => response.json())
    .then(data => {
      // ESG Reports
      const esgTable = document.getElementById('esg-reports-table');
      if (esgTable) {
        esgTable.innerHTML = '';
        
        data.esgReports.forEach(report => {
          const row = document.createElement('tr');
          
          // Determine score class
          let scoreClass = 'badge-warning';
          if (report.score >= 80) {
            scoreClass = 'badge-success';
          } else if (report.score < 60) {
            scoreClass = 'badge-danger';
          }
          
          row.innerHTML = `
            <td>${report.title}</td>
            <td>${report.date}</td>
            <td><span class="badge ${scoreClass}">${report.score}</span></td>
            <td>${report.status}</td>
            <td>
              <button class="btn btn-sm btn-outline" onclick="viewReport('${report.id}')">View Report</button>
            </td>
          `;
          
          esgTable.appendChild(row);
        });
      }
      
      // Regulatory Compliance
      const regulatoryTable = document.getElementById('regulatory-compliance-table');
      if (regulatoryTable) {
        regulatoryTable.innerHTML = '';
        
        data.regulatoryCompliance.forEach(item => {
          const row = document.createElement('tr');
          
          // Determine status class
          let statusClass = 'badge-warning';
          if (item.status === 'Compliant') {
            statusClass = 'badge-success';
          } else if (item.status === 'Non-Compliant') {
            statusClass = 'badge-danger';
          }
          
          row.innerHTML = `
            <td>${item.regulation}</td>
            <td><span class="badge ${statusClass}">${item.status}</span></td>
            <td>${item.lastAudit}</td>
          `;
          
          regulatoryTable.appendChild(row);
        });
      }
    })
    .catch(error => {
      console.error('Error loading compliance reports:', error);
      showErrorMessage('compliance-reports-container', 'Failed to load compliance reports');
    });
}

// Load auto contracts from API
function loadAutoContracts() {
  fetch('/api/auto-contracts')
    .then(response => response.json())
    .then(data => {
      // Deployed Contracts
      const contractsTable = document.getElementById('contracts-table');
      if (contractsTable) {
        contractsTable.innerHTML = '';
        
        data.deployedContracts.forEach(contract => {
          const row = document.createElement('tr');
          
          // Determine status class
          let statusClass = 'badge-warning';
          if (contract.status === 'Active') {
            statusClass = 'badge-success';
          } else if (contract.status === 'Failed') {
            statusClass = 'badge-danger';
          }
          
          row.innerHTML = `
            <td>${contract.id}</td>
            <td>${contract.name}</td>
            <td><code>${contract.address}</code></td>
            <td><span class="badge ${statusClass}">${contract.status}</span></td>
            <td>
              <button class="btn btn-sm btn-outline" onclick="viewContractDetails('${contract.id}')">View Details</button>
            </td>
          `;
          
          contractsTable.appendChild(row);
        });
      }
      
      // Reward Distributions
      const distributionsTable = document.getElementById('distributions-table');
      if (distributionsTable) {
        distributionsTable.innerHTML = '';
        
        data.rewardDistributions.forEach(dist => {
          const row = document.createElement('tr');
          
          row.innerHTML = `
            <td>${dist.date}</td>
            <td>${dist.amount}</td>
            <td>${dist.recipients}</td>
            <td><code>${dist.txHash}</code></td>
            <td>
              <button class="btn btn-sm btn-outline" onclick="viewTransactionDetails('${dist.txHash}')">View Transaction</button>
            </td>
          `;
          
          distributionsTable.appendChild(row);
        });
      }
    })
    .catch(error => {
      console.error('Error loading auto contracts:', error);
      showErrorMessage('auto-contracts-container', 'Failed to load auto contracts');
    });
}

// Load ZK verifications from API
function loadZkVerifications() {
  fetch('/api/zk-verifications')
    .then(response => response.json())
    .then(data => {
      const verifiedTable = document.getElementById('zk-verifications-table');
      if (!verifiedTable) return;
      
      verifiedTable.innerHTML = '';
      
      data.verifiedProofs.forEach(proof => {
        const row = document.createElement('tr');
        
        // Determine status class
        let statusClass = 'badge-warning';
        if (proof.status === 'Verified') {
          statusClass = 'badge-success';
        } else if (proof.status === 'Rejected') {
          statusClass = 'badge-danger';
        }
        
        row.innerHTML = `
          <td>${proof.id}</td>
          <td>${proof.type}</td>
          <td>${proof.date}</td>
          <td><span class="badge ${statusClass}">${proof.status}</span></td>
          <td>
            <button class="btn btn-sm btn-outline" onclick="viewProofDetails('${proof.id}')">View Proof</button>
          </td>
        `;
        
        verifiedTable.appendChild(row);
      });
    })
    .catch(error => {
      console.error('Error loading ZK verifications:', error);
      showErrorMessage('zk-verifications-container', 'Failed to load ZK verifications');
    });
}

// Set up test features
function setupTestFeatures() {
  // Sustainability Score Test
  const scoreForm = document.getElementById('test-score-form');
  if (scoreForm) {
    scoreForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const operationName = document.getElementById('operation-name').value;
      const energySource = document.getElementById('energy-source').value;
      const energyEfficiency = parseFloat(document.getElementById('energy-efficiency').value);
      
      // Calculate mock score
      let score = 50; // Base score
      
      // Add points for renewable energy sources
      if (energySource === 'solar') score += 30;
      else if (energySource === 'wind') score += 25;
      else if (energySource === 'hydro') score += 20;
      else if (energySource === 'geothermal') score += 15;
      
      // Add points for energy efficiency
      score += energyEfficiency * 10;
      
      // Cap score at 100
      score = Math.min(100, Math.round(score));
      
      // Display result
      const resultContainer = document.getElementById('score-result');
      
      let scoreClass = 'badge-warning';
      if (score >= 80) {
        scoreClass = 'badge-success';
      } else if (score < 60) {
        scoreClass = 'badge-danger';
      }
      
      resultContainer.innerHTML = `
        <h4>Sustainability Score Result</h4>
        <p>Operation: <strong>${operationName}</strong></p>
        <p>Energy Source: <strong>${energySource.charAt(0).toUpperCase() + energySource.slice(1)}</strong></p>
        <p>Energy Efficiency: <strong>${energyEfficiency}</strong></p>
        <p>Score: <span class="badge ${scoreClass}">${score}</span></p>
        <p>This operation would ${score >= 70 ? 'qualify' : 'not qualify'} for EcoChain rewards.</p>
      `;
      
      resultContainer.style.display = 'block';
    });
  }
  
  // Optimization Test
  const optimizationForm = document.getElementById('test-optimization-form');
  if (optimizationForm) {
    optimizationForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const currentHardware = document.getElementById('current-hardware').value;
      const powerConsumption = parseFloat(document.getElementById('power-consumption').value);
      const coolingSystem = document.getElementById('cooling-system').value;
      
      // Generate mock recommendations
      const resultContainer = document.getElementById('optimization-result');
      
      resultContainer.innerHTML = `
        <h4>Optimization Recommendations</h4>
        <div class="mb-3">
          <h5>Hardware Recommendations</h5>
          <p>${getHardwareRecommendation(currentHardware)}</p>
        </div>
        <div class="mb-3">
          <h5>Energy Recommendations</h5>
          <p>${getEnergyRecommendation(powerConsumption)}</p>
        </div>
        <div class="mb-3">
          <h5>Cooling Recommendations</h5>
          <p>${getCoolingRecommendation(coolingSystem)}</p>
        </div>
        <p>Estimated Annual Savings: $${Math.round(powerConsumption * 365 * 0.12 * 0.25)}</p>
      `;
      
      resultContainer.style.display = 'block';
    });
  }
  
  // Smart Contract Test
  const contractForm = document.getElementById('test-contract-form');
  if (contractForm) {
    contractForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const contractType = document.getElementById('contract-type').value;
      const rewardAmount = parseFloat(document.getElementById('reward-amount').value);
      const recipients = parseInt(document.getElementById('recipients').value);
      
      // Generate mock contract deployment
      const resultContainer = document.getElementById('contract-result');
      
      const contractAddress = '0x' + Array(40).fill(0).map(() => 
        Math.floor(Math.random() * 16).toString(16)).join('');
      
      const txHash = '0x' + Array(64).fill(0).map(() => 
        Math.floor(Math.random() * 16).toString(16)).join('');
      
      resultContainer.innerHTML = `
        <h4>Contract Deployment Result</h4>
        <p>Contract Type: <strong>${contractType}</strong></p>
        <p>Contract Address: <code>${contractAddress}</code></p>
        <p>Transaction Hash: <code>${txHash}</code></p>
        <p>Reward Amount: <strong>${rewardAmount} ECO</strong></p>
        <p>Recipients: <strong>${recipients}</strong></p>
        <p>Status: <span class="badge badge-success">Success</span></p>
        <p>Gas Used: <strong>${Math.round(210000 + Math.random() * 50000)}</strong></p>
      `;
      
      resultContainer.style.display = 'block';
    });
  }
}

// Set up charts
function setupCharts() {
  // Only set up charts if Chart.js is loaded and containers exist
  if (typeof Chart === 'undefined') {
    console.warn('Chart.js not loaded');
    return;
  }
  
  // Energy Forecast Chart
  const energyForecastCanvas = document.getElementById('energy-forecast-chart');
  if (energyForecastCanvas) {
    window.energyForecastChart = new Chart(energyForecastCanvas, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Predicted Energy Usage (kWh)',
            data: [],
            borderColor: '#1E88E5',
            backgroundColor: 'rgba(30, 136, 229, 0.1)',
            borderWidth: 2,
            tension: 0.3,
            fill: true
          },
          {
            label: 'Actual Energy Usage (kWh)',
            data: [],
            borderColor: '#34A853',
            backgroundColor: 'rgba(52, 168, 83, 0.1)',
            borderWidth: 2,
            tension: 0.3,
            fill: true
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip: {
            mode: 'index',
            intersect: false,
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Month'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Energy Usage (kWh)'
            },
            beginAtZero: true
          }
        }
      }
    });
    
    // If we have data, update the chart
    if (window.analyticsData && window.analyticsData.energyUsageForecast) {
      updateEnergyForecastChart(window.analyticsData.energyUsageForecast);
    }
  }
}

// Update energy forecast chart with data
function updateEnergyForecastChart(data) {
  if (!window.energyForecastChart) return;
  
  const labels = data.map(item => item.month);
  const predictedData = data.map(item => item.predicted);
  const actualData = data.map(item => item.actual);
  
  window.energyForecastChart.data.labels = labels;
  window.energyForecastChart.data.datasets[0].data = predictedData;
  window.energyForecastChart.data.datasets[1].data = actualData;
  window.energyForecastChart.update();
}

// Helper function to show error messages
function showErrorMessage(containerId, message) {
  const container = document.getElementById(containerId);
  if (container) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.textContent = message;
    
    container.prepend(errorDiv);
    
    // Remove after 5 seconds
    setTimeout(() => {
      errorDiv.remove();
    }, 5000);
  }
}

// Mock recommendation functions
function getHardwareRecommendation(currentHardware) {
  const recommendations = {
    'asic': 'Upgrade to Bitmain Antminer S19 XP for 30% efficiency improvement. ROI: 8 months.',
    'gpu': 'Implement GPU undervolting and optimize memory clock settings. Potential 15% power reduction. ROI: 1 month.',
    'cpu': 'Consider switching to specialized ASIC hardware for 400% efficiency improvement. ROI: 6 months.',
    'mixed': 'Consolidate to standardized ASIC hardware for simplified maintenance and better efficiency. ROI: 10 months.'
  };
  
  return recommendations[currentHardware] || 'Upgrade to more energy-efficient hardware models. ROI: 12 months.';
}

function getEnergyRecommendation(powerConsumption) {
  if (powerConsumption < 100) {
    return 'Consider solar panel installation with 5kW capacity. ROI: 36 months.';
  } else if (powerConsumption < 500) {
    return 'Implement 20kW solar array with battery storage. ROI: 30 months.';
  } else {
    return 'Explore power purchase agreements with renewable energy providers and implement 100kW solar installation. ROI: 24 months.';
  }
}

function getCoolingRecommendation(coolingSystem) {
  const recommendations = {
    'air': 'Upgrade to liquid cooling system for 35% cooling efficiency improvement. ROI: 14 months.',
    'liquid': 'Optimize pump speeds and implement heat recovery system to reuse waste heat. ROI: 10 months.',
    'immersion': 'Implement heat recovery system to reuse waste heat for building heating or water heating. ROI: 18 months.',
    'none': 'Implement basic air cooling with proper ventilation and airflow management. ROI: 3 months.'
  };
  
  return recommendations[coolingSystem] || 'Implement advanced cooling management system with temperature zoning. ROI: 12 months.';
}

// Placeholder functions for detail views
function viewOperationDetails(id) {
  alert(`Viewing details for operation ID: ${id}\nThis feature would show detailed metrics and history.`);
}

function viewReport(id) {
  alert(`Viewing report: ${id}\nThis feature would display the full ESG report.`);
}

function viewContractDetails(id) {
  alert(`Viewing contract details: ${id}\nThis feature would show contract code, transactions, and status.`);
}

function viewTransactionDetails(txHash) {
  alert(`Viewing transaction: ${txHash}\nThis feature would show transaction details from the blockchain.`);
}

function viewProofDetails(id) {
  alert(`Viewing proof details: ${id}\nThis feature would show the zero-knowledge proof verification details.`);
} 