// EcoChain Guardian Demo - Modal Functionality

// Modal management system
const ModalSystem = {
  // Store active modals
  activeModals: [],
  
  // Create a new modal
  create: function(options) {
    // Default options
    const defaults = {
      id: `modal-${Date.now()}`,
      title: 'Modal Title',
      content: '',
      size: 'medium', // small, medium, large
      buttons: [],
      onClose: null
    };
    
    // Merge options with defaults
    const settings = {...defaults, ...options};
    
    // Create modal HTML
    const modalHTML = `
      <div id="${settings.id}-overlay" class="modal-overlay">
        <div id="${settings.id}" class="modal ${settings.size}">
          <div class="modal-header">
            <h3 class="modal-title">${settings.title}</h3>
            <button type="button" class="modal-close" data-dismiss="modal" aria-label="Close">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            ${settings.content}
          </div>
          ${settings.buttons.length > 0 ? `
          <div class="modal-footer">
            ${settings.buttons.map(btn => `
              <button type="button" class="btn ${btn.class || 'btn-outline'}" data-action="${btn.action || ''}">${btn.text}</button>
            `).join('')}
          </div>
          ` : ''}
        </div>
      </div>
    `;
    
    // Add modal to the DOM
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Get modal elements
    const modalOverlay = document.getElementById(`${settings.id}-overlay`);
    const modal = document.getElementById(settings.id);
    const closeBtn = modal.querySelector('.modal-close');
    
    // Add event listeners
    closeBtn.addEventListener('click', () => {
      this.close(settings.id);
      if (settings.onClose && typeof settings.onClose === 'function') {
        settings.onClose();
      }
    });
    
    // Add event listeners to buttons
    if (settings.buttons.length > 0) {
      const buttons = modal.querySelectorAll('.modal-footer .btn');
      buttons.forEach((btn, index) => {
        btn.addEventListener('click', () => {
          const action = btn.getAttribute('data-action');
          if (settings.buttons[index].callback && typeof settings.buttons[index].callback === 'function') {
            settings.buttons[index].callback();
          }
          if (action === 'close') {
            this.close(settings.id);
          }
        });
      });
    }
    
    // Close when clicking outside the modal
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) {
        this.close(settings.id);
        if (settings.onClose && typeof settings.onClose === 'function') {
          settings.onClose();
        }
      }
    });
    
    // Add to active modals
    this.activeModals.push(settings.id);
    
    // Return modal ID
    return settings.id;
  },
  
  // Open a modal
  open: function(id) {
    const modalOverlay = document.getElementById(`${id}-overlay`);
    if (modalOverlay) {
      // Add active class to show modal with animation
      modalOverlay.classList.add('active');
      
      // Prevent body scrolling
      document.body.style.overflow = 'hidden';
    }
  },
  
  // Close a modal
  close: function(id) {
    const modalOverlay = document.getElementById(`${id}-overlay`);
    if (modalOverlay) {
      // Remove active class to hide modal with animation
      modalOverlay.classList.remove('active');
      
      // Remove modal from DOM after animation
      setTimeout(() => {
        modalOverlay.remove();
        
        // Remove from active modals
        const index = this.activeModals.indexOf(id);
        if (index > -1) {
          this.activeModals.splice(index, 1);
        }
        
        // Restore body scrolling if no modals are open
        if (this.activeModals.length === 0) {
          document.body.style.overflow = '';
        }
      }, 300);
    }
  },
  
  // Close all modals
  closeAll: function() {
    // Create a copy of the array to avoid issues when removing items
    const modals = [...this.activeModals];
    modals.forEach(id => {
      this.close(id);
    });
  }
};

// Contract Details Modal
function showContractDetails(contractId) {
  // Get contract data (in a real app, this would be fetched from an API)
  const contractData = getContractById(contractId);
  
  if (!contractData) return;
  
  // Create contract code sample
  const contractCode = `// EcoRewards Distribution Contract
pragma solidity ^0.8.0;

contract EcoRewards {
    address public owner;
    uint256 public totalRewards;
    mapping(address => uint256) public scores;
    mapping(address => uint256) public rewards;
    
    event RewardDistributed(address recipient, uint256 amount);
    
    constructor() {
        owner = msg.sender;
    }
    
    function updateScore(address operation, uint256 score) public {
        require(msg.sender == owner, "Only owner can update scores");
        scores[operation] = score;
    }
    
    function distributeRewards() public {
        require(msg.sender == owner, "Only owner can distribute rewards");
        // Distribution logic here
    }
}`;

  // Create timeline data
  const timeline = [
    {
      date: '2024-03-15 14:32:45',
      title: 'Contract Deployed',
      description: 'Contract successfully deployed to Ethereum mainnet'
    },
    {
      date: '2024-03-15 14:35:12',
      title: 'Owner Set',
      description: 'Contract ownership transferred to EcoChain Guardian multisig wallet'
    },
    {
      date: '2024-03-20 09:15:33',
      title: 'Scores Updated',
      description: 'Sustainability scores updated for 42 mining operations'
    },
    {
      date: '2024-03-25 11:22:05',
      title: 'Rewards Distributed',
      description: 'First reward distribution completed to 42 recipients'
    }
  ];
  
  // Create modal content
  const content = `
    <div class="contract-details">
      <div>
        <div class="contract-details-section">
          <h4 class="contract-details-title">Contract Information</h4>
          <div class="transaction-details">
            <div class="transaction-row">
              <div class="transaction-label">Contract ID</div>
              <div class="transaction-value">${contractData.id}</div>
            </div>
            <div class="transaction-row">
              <div class="transaction-label">Name</div>
              <div class="transaction-value">${contractData.name}</div>
            </div>
            <div class="transaction-row">
              <div class="transaction-label">Address</div>
              <div class="transaction-value transaction-hash">${contractData.address}</div>
            </div>
            <div class="transaction-row">
              <div class="transaction-label">Status</div>
              <div class="transaction-value">
                <span class="badge badge-${contractData.status === 'Active' ? 'success' : contractData.status === 'Pending' ? 'warning' : 'danger'}">
                  ${contractData.status}
                </span>
              </div>
            </div>
            <div class="transaction-row">
              <div class="transaction-label">Created</div>
              <div class="transaction-value">March 15, 2024</div>
            </div>
            <div class="transaction-row">
              <div class="transaction-label">Last Updated</div>
              <div class="transaction-value">March 25, 2024</div>
            </div>
          </div>
        </div>
        
        <div class="contract-details-section">
          <h4 class="contract-details-title">Contract Code</h4>
          <div class="contract-code">${contractCode}</div>
        </div>
      </div>
      
      <div>
        <div class="contract-details-section">
          <h4 class="contract-details-title">Contract Timeline</h4>
          <ul class="contract-timeline">
            ${timeline.map(item => `
              <li class="timeline-item">
                <div class="timeline-date">${item.date}</div>
                <div class="timeline-title">${item.title}</div>
                <div class="timeline-description">${item.description}</div>
              </li>
            `).join('')}
          </ul>
        </div>
        
        <div class="contract-details-section">
          <h4 class="contract-details-title">Contract Metrics</h4>
          <div class="transaction-details">
            <div class="transaction-row">
              <div class="transaction-label">Total Rewards</div>
              <div class="transaction-value">125,000 ECO</div>
            </div>
            <div class="transaction-row">
              <div class="transaction-label">Recipients</div>
              <div class="transaction-value">42</div>
            </div>
            <div class="transaction-row">
              <div class="transaction-label">Average Score</div>
              <div class="transaction-value">83.5</div>
            </div>
            <div class="transaction-row">
              <div class="transaction-label">Gas Used</div>
              <div class="transaction-value">3.2 ETH</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Create and open modal
  const modalId = ModalSystem.create({
    title: `Contract Details: ${contractData.name}`,
    content: content,
    size: 'large',
    buttons: [
      {
        text: 'View on Etherscan',
        class: 'btn-secondary',
        callback: () => {
          window.open(`https://etherscan.io/address/${contractData.address}`, '_blank');
        }
      },
      {
        text: 'Close',
        class: 'btn-outline',
        action: 'close'
      }
    ]
  });
  
  ModalSystem.open(modalId);
}

// Transaction Details Modal
function showTransactionDetails(txHash) {
  // In a real app, this would fetch transaction data from the blockchain
  const txData = {
    hash: txHash,
    blockNumber: 17542983,
    timestamp: '2024-03-15 11:22:05',
    from: '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
    to: '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
    value: '0 ETH',
    gasUsed: '245,320',
    status: 'Success'
  };
  
  // Create modal content
  const content = `
    <div class="transaction-details">
      <div class="transaction-row">
        <div class="transaction-label">Transaction Hash</div>
        <div class="transaction-value transaction-hash">${txData.hash}</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">Block</div>
        <div class="transaction-value">${txData.blockNumber}</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">Timestamp</div>
        <div class="transaction-value">${txData.timestamp}</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">From</div>
        <div class="transaction-value transaction-hash">${txData.from}</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">To</div>
        <div class="transaction-value transaction-hash">${txData.to}</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">Value</div>
        <div class="transaction-value">${txData.value}</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">Gas Used</div>
        <div class="transaction-value">${txData.gasUsed}</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">Status</div>
        <div class="transaction-value">
          <span class="badge badge-success">${txData.status}</span>
        </div>
      </div>
    </div>
    
    <div class="contract-details-section">
      <h4 class="contract-details-title">Transaction Data</h4>
      <div class="contract-code">0x7ff36ab500000000000000000000000000000000000000000000000008a1edd263a25600000000000000000000000000000000000000000000000000000000000000000000000000000000000000007a250d5630b4cf539739df2c5dacb4c659f2488d000000000000000000000000000000000000000000000000000000006423a03d</div>
    </div>
  `;
  
  // Create and open modal
  const modalId = ModalSystem.create({
    title: 'Transaction Details',
    content: content,
    buttons: [
      {
        text: 'View on Etherscan',
        class: 'btn-secondary',
        callback: () => {
          window.open(`https://etherscan.io/tx/${txHash}`, '_blank');
        }
      },
      {
        text: 'Close',
        class: 'btn-outline',
        action: 'close'
      }
    ]
  });
  
  ModalSystem.open(modalId);
}

// Distribution Details Modal
function showDistributionDetails(txHash) {
  // In a real app, this would fetch distribution data from the blockchain
  const distributionData = {
    txHash: txHash,
    date: '2024-03-15',
    amount: '125,000 ECO',
    recipients: 42,
    topRecipients: [
      { address: '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984', amount: '12,500 ECO' },
      { address: '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D', amount: '10,750 ECO' },
      { address: '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f', amount: '9,800 ECO' },
      { address: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', amount: '8,200 ECO' },
      { address: '0x6B175474E89094C44Da98b954EedeAC495271d0F', amount: '7,500 ECO' }
    ]
  };
  
  // Create modal content
  const content = `
    <div class="transaction-details mb-4">
      <div class="transaction-row">
        <div class="transaction-label">Distribution Date</div>
        <div class="transaction-value">${distributionData.date}</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">Total Amount</div>
        <div class="transaction-value">${distributionData.amount}</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">Recipients</div>
        <div class="transaction-value">${distributionData.recipients}</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">Transaction Hash</div>
        <div class="transaction-value transaction-hash">${distributionData.txHash}</div>
      </div>
    </div>
    
    <div class="contract-details-section">
      <h4 class="contract-details-title">Distribution Chart</h4>
      <div class="distribution-chart">
        <canvas id="distribution-chart"></canvas>
      </div>
    </div>
    
    <div class="contract-details-section">
      <h4 class="contract-details-title">Top Recipients</h4>
      <div class="recipient-list">
        ${distributionData.topRecipients.map(recipient => `
          <div class="recipient-item">
            <div class="recipient-address">${recipient.address}</div>
            <div class="recipient-amount">${recipient.amount}</div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
  
  // Create and open modal
  const modalId = ModalSystem.create({
    title: 'Reward Distribution Details',
    content: content,
    size: 'large',
    buttons: [
      {
        text: 'View All Recipients',
        class: 'btn-secondary',
        callback: () => {
          alert('In a real app, this would show all 42 recipients');
        }
      },
      {
        text: 'Export Data',
        class: 'btn-outline',
        callback: () => {
          alert('In a real app, this would export distribution data');
        }
      },
      {
        text: 'Close',
        class: 'btn-outline',
        action: 'close'
      }
    ],
    onClose: () => {
      // Clean up chart if it was created
      if (window.distributionChart) {
        window.distributionChart.destroy();
        window.distributionChart = null;
      }
    }
  });
  
  ModalSystem.open(modalId);
  
  // Create chart after modal is open
  setTimeout(() => {
    const chartCanvas = document.getElementById('distribution-chart');
    if (chartCanvas && typeof Chart !== 'undefined') {
      window.distributionChart = new Chart(chartCanvas, {
        type: 'pie',
        data: {
          labels: ['Top 5 Recipients', 'Other Recipients'],
          datasets: [{
            data: [48750, 76250],
            backgroundColor: [
              '#34A853',
              '#1E88E5'
            ],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || '';
                  const value = context.raw;
                  const percentage = Math.round((value / 125000) * 100);
                  return `${label}: ${value} ECO (${percentage}%)`;
                }
              }
            }
          }
        }
      });
    }
  }, 300);
}

// Proof Details Modal
function showProofDetails(proofId) {
  // In a real app, this would fetch proof data from the blockchain
  const proofData = {
    id: proofId,
    type: 'Renewable Energy Certificate',
    date: '2024-03-01',
    status: 'Verified',
    issuer: 'EcoChain Guardian ZK Verifier',
    verifier: '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
    operation: 'Mining Operation B',
    energySource: 'Wind',
    energyAmount: '2,500 MWh',
    carbonOffset: '1,875 tons CO2e'
  };
  
  // Create modal content
  const content = `
    <div class="proof-details">
             <div class="proof-verification">
         <div class="verification-icon">
           <i class="fas fa-shield-alt"></i>
         </div>
        <div class="verification-content">
          <div class="verification-title">Zero-Knowledge Proof Verified</div>
          <p>This proof has been cryptographically verified without revealing sensitive operational data.</p>
        </div>
      </div>
      
      <div class="transaction-details">
        <div class="transaction-row">
          <div class="transaction-label">Proof ID</div>
          <div class="transaction-value">${proofData.id}</div>
        </div>
        <div class="transaction-row">
          <div class="transaction-label">Type</div>
          <div class="transaction-value">${proofData.type}</div>
        </div>
        <div class="transaction-row">
          <div class="transaction-label">Date</div>
          <div class="transaction-value">${proofData.date}</div>
        </div>
        <div class="transaction-row">
          <div class="transaction-label">Status</div>
          <div class="transaction-value">
            <span class="badge badge-success">${proofData.status}</span>
          </div>
        </div>
        <div class="transaction-row">
          <div class="transaction-label">Issuer</div>
          <div class="transaction-value">${proofData.issuer}</div>
        </div>
        <div class="transaction-row">
          <div class="transaction-label">Verifier Address</div>
          <div class="transaction-value transaction-hash">${proofData.verifier}</div>
        </div>
      </div>
      
      <div class="contract-details-section">
        <h4 class="contract-details-title">Verified Claims</h4>
        <div class="transaction-details">
          <div class="transaction-row">
            <div class="transaction-label">Operation</div>
            <div class="transaction-value">${proofData.operation}</div>
          </div>
          <div class="transaction-row">
            <div class="transaction-label">Energy Source</div>
            <div class="transaction-value">${proofData.energySource}</div>
          </div>
          <div class="transaction-row">
            <div class="transaction-label">Energy Amount</div>
            <div class="transaction-value">${proofData.energyAmount}</div>
          </div>
          <div class="transaction-row">
            <div class="transaction-label">Carbon Offset</div>
            <div class="transaction-value">${proofData.carbonOffset}</div>
          </div>
        </div>
      </div>
      
      <div class="contract-details-section">
        <h4 class="contract-details-title">Zero-Knowledge Proof</h4>
        <div class="contract-code">
{
  "pi_a": [
    "16225832717485425251341210697647798563022595209436102621017586539376466920359",
    "5865271993585825160566107110121034082348117188663282651357551912585902198744",
    "1"
  ],
  "pi_b": [
    [
      "10158533400077786424793413799696128205143463986648572523210599573966285068047",
      "17897835224440345012834096818584649431866220592938906214015407767624742020757"
    ],
    [
      "16178510563055509814618991336471520285089372429398503061279709299618366906679",
      "21854282271639129657903749255642615149118845227184112387533903861093905249035"
    ],
    [
      "1",
      "0"
    ]
  ],
  "pi_c": [
    "19798971325910932754130995511928043514517389593701157597990265922249493431406",
    "6346869635521037615261884798198612689948962205504487721987520078543155157803",
    "1"
  ],
  "protocol": "groth16",
  "curve": "bn128"
}
        </div>
      </div>
    </div>
  `;
  
  // Create and open modal
  const modalId = ModalSystem.create({
    title: `Zero-Knowledge Proof: ${proofData.id}`,
    content: content,
    size: 'large',
    buttons: [
      {
        text: 'Verify on Chain',
        class: 'btn-secondary',
        callback: () => {
          alert('In a real app, this would verify the proof on-chain');
        }
      },
      {
        text: 'Export Certificate',
        class: 'btn-outline',
        callback: () => {
          alert('In a real app, this would export a certificate');
        }
      },
      {
        text: 'Close',
        class: 'btn-outline',
        action: 'close'
      }
    ]
  });
  
  ModalSystem.open(modalId);
}

// Helper function to get contract by ID
function getContractById(id) {
  // In a real app, this would fetch from an API
  const contracts = {
    'ECR-001': { id: 'ECR-001', name: 'EcoRewards Distribution', address: '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D', status: 'Active' },
    'EST-002': { id: 'EST-002', name: 'EcoStaking Pool', address: '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f', status: 'Active' },
    'EGV-003': { id: 'EGV-003', name: 'EcoGovernance Voting', address: '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984', status: 'Pending' }
  };
  
  return contracts[id];
}

// Deploy Contract Modal
function showDeployContractModal() {
  // Create modal content
  const content = `
    <form id="deploy-contract-form">
      <div class="form-group">
        <label class="form-label" for="contract-template">Contract Template</label>
        <select class="form-select" id="contract-template" required>
          <option value="">Select Contract Template</option>
          <option value="rewards">EcoRewards Distribution</option>
          <option value="staking">EcoStaking Pool</option>
          <option value="governance">EcoGovernance Voting</option>
        </select>
      </div>
      
      <div class="form-group">
        <label class="form-label" for="contract-name">Contract Name</label>
        <input type="text" class="form-control" id="contract-name" placeholder="e.g., Q2 2024 Rewards Distribution" required>
      </div>
      
      <div class="form-group">
        <label class="form-label" for="initial-funding">Initial Funding (ECO Tokens)</label>
        <input type="number" class="form-control" id="initial-funding" min="1000" value="100000" required>
      </div>
      
      <div class="form-group">
        <label class="form-label" for="min-score">Minimum Qualifying Score</label>
        <input type="number" class="form-control" id="min-score" min="0" max="100" value="70" required>
      </div>
      
      <div class="form-group">
        <label class="form-label" for="network">Blockchain Network</label>
        <select class="form-select" id="network" required>
          <option value="ethereum">Ethereum Mainnet</option>
          <option value="polygon">Polygon</option>
          <option value="optimism">Optimism</option>
          <option value="arbitrum">Arbitrum</option>
        </select>
      </div>
      
      <div class="form-group">
        <label class="form-label">Advanced Options</label>
        <div class="form-check">
          <input class="form-check-input" type="checkbox" id="auto-distribution">
          <label class="form-check-label" for="auto-distribution">Enable Automatic Distribution</label>
        </div>
        <div class="form-check">
          <input class="form-check-input" type="checkbox" id="use-multisig">
          <label class="form-check-label" for="use-multisig">Use Multisig Wallet</label>
        </div>
      </div>
    </form>
  `;
  
  // Create and open modal
  const modalId = ModalSystem.create({
    title: 'Deploy New Contract',
    content: content,
    buttons: [
      {
        text: 'Deploy Contract',
        class: 'btn-primary',
        callback: () => {
          const form = document.getElementById('deploy-contract-form');
          if (form.checkValidity()) {
            const template = document.getElementById('contract-template').value;
            const name = document.getElementById('contract-name').value;
            const funding = document.getElementById('initial-funding').value;
            
            // Show success message
            ModalSystem.closeAll();
            showDeploymentSuccessModal(name, funding);
          } else {
            form.reportValidity();
          }
        }
      },
      {
        text: 'Cancel',
        class: 'btn-outline',
        action: 'close'
      }
    ]
  });
  
  ModalSystem.open(modalId);
}

// Contract Deployment Success Modal
function showDeploymentSuccessModal(name, funding) {
  // Generate mock contract address
  const contractAddress = '0x' + Array(40).fill(0).map(() => 
    Math.floor(Math.random() * 16).toString(16)).join('');
  
  // Create modal content
  const content = `
    <div class="text-center mb-4">
      <div style="font-size: 4rem; color: var(--primary); margin-bottom: 1rem;">
        <i class="fas fa-check-circle"></i>
      </div>
      <h4>Contract Deployed Successfully!</h4>
    </div>
    
    <div class="transaction-details">
      <div class="transaction-row">
        <div class="transaction-label">Contract Name</div>
        <div class="transaction-value">${name}</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">Contract Address</div>
        <div class="transaction-value transaction-hash">${contractAddress}</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">Initial Funding</div>
        <div class="transaction-value">${funding} ECO</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">Status</div>
        <div class="transaction-value">
          <span class="badge badge-success">Active</span>
        </div>
      </div>
    </div>
  `;
  
  // Create and open modal
  const modalId = ModalSystem.create({
    title: 'Deployment Successful',
    content: content,
    buttons: [
      {
        text: 'View Contract Details',
        class: 'btn-secondary',
        callback: () => {
          ModalSystem.closeAll();
          showContractDetails('ECR-001'); // Just show a sample contract for demo
        }
      },
      {
        text: 'Close',
        class: 'btn-outline',
        action: 'close'
      }
    ]
  });
  
  ModalSystem.open(modalId);
  
  // Refresh the contracts table - in a real app, this would call an API
  // For demo, we'll just reload the page after a delay
  setTimeout(() => {
    window.location.reload();
  }, 3000);
}

// Schedule Distribution Modal
function showScheduleDistributionModal() {
  // Create modal content
  const content = `
    <form id="schedule-distribution-form">
      <div class="form-group">
        <label class="form-label" for="distribution-contract">Contract</label>
        <select class="form-select" id="distribution-contract" required>
          <option value="">Select Contract</option>
          <option value="ECR-001">ECR-001: EcoRewards Distribution</option>
          <option value="EST-002">EST-002: EcoStaking Pool</option>
        </select>
      </div>
      
      <div class="form-group">
        <label class="form-label" for="distribution-date">Distribution Date</label>
        <input type="date" class="form-control" id="distribution-date" required>
      </div>
      
      <div class="form-group">
        <label class="form-label" for="distribution-amount">Amount to Distribute (ECO Tokens)</label>
        <input type="number" class="form-control" id="distribution-amount" min="1000" value="50000" required>
      </div>
      
      <div class="form-group">
        <label class="form-label" for="distribution-criteria">Distribution Criteria</label>
        <select class="form-select" id="distribution-criteria" required>
          <option value="score">Proportional to Sustainability Score</option>
          <option value="equal">Equal Distribution</option>
          <option value="weighted">Weighted by Mining Power</option>
        </select>
      </div>
      
      <div class="form-group">
        <label class="form-label">Advanced Options</label>
        <div class="form-check">
          <input class="form-check-input" type="checkbox" id="require-verification">
          <label class="form-check-label" for="require-verification">Require ZK Verification</label>
        </div>
        <div class="form-check">
          <input class="form-check-input" type="checkbox" id="recurring-distribution">
          <label class="form-check-label" for="recurring-distribution">Make Recurring (Monthly)</label>
        </div>
      </div>
    </form>
  `;
  
  // Create and open modal
  const modalId = ModalSystem.create({
    title: 'Schedule Reward Distribution',
    content: content,
    buttons: [
      {
        text: 'Schedule Distribution',
        class: 'btn-primary',
        callback: () => {
          const form = document.getElementById('schedule-distribution-form');
          if (form.checkValidity()) {
            const contract = document.getElementById('distribution-contract').value;
            const amount = document.getElementById('distribution-amount').value;
            
            // Show success message
            ModalSystem.closeAll();
            showScheduleSuccessModal(contract, amount);
          } else {
            form.reportValidity();
          }
        }
      },
      {
        text: 'Cancel',
        class: 'btn-outline',
        action: 'close'
      }
    ]
  });
  
  ModalSystem.open(modalId);
  
  // Set default date to tomorrow
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  document.getElementById('distribution-date').valueAsDate = tomorrow;
}

// Schedule Success Modal
function showScheduleSuccessModal(contractId, amount) {
  // Get contract data
  const contractData = getContractById(contractId);
  if (!contractData) return;
  
  // Format date
  const date = new Date();
  date.setDate(date.getDate() + 1);
  const formattedDate = date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  
  // Create modal content
  const content = `
    <div class="text-center mb-4">
      <div style="font-size: 4rem; color: var(--primary); margin-bottom: 1rem;">
        <i class="fas fa-calendar-check"></i>
      </div>
      <h4>Distribution Scheduled Successfully!</h4>
    </div>
    
    <div class="transaction-details">
      <div class="transaction-row">
        <div class="transaction-label">Contract</div>
        <div class="transaction-value">${contractData.id}: ${contractData.name}</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">Distribution Date</div>
        <div class="transaction-value">${formattedDate}</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">Amount</div>
        <div class="transaction-value">${amount} ECO</div>
      </div>
      <div class="transaction-row">
        <div class="transaction-label">Estimated Recipients</div>
        <div class="transaction-value">42</div>
      </div>
    </div>
    
    <div class="alert alert-info mt-3">
      <i class="fas fa-info-circle"></i> The distribution will be processed automatically on the scheduled date. You can cancel or modify this distribution from the contract details page.
    </div>
  `;
  
  // Create and open modal
  const modalId = ModalSystem.create({
    title: 'Distribution Scheduled',
    content: content,
    buttons: [
      {
        text: 'View Contract Details',
        class: 'btn-secondary',
        callback: () => {
          ModalSystem.closeAll();
          showContractDetails(contractId);
        }
      },
      {
        text: 'Close',
        class: 'btn-outline',
        action: 'close'
      }
    ]
  });
  
  ModalSystem.open(modalId);
}

// Add event listener for workflow info button
document.addEventListener('DOMContentLoaded', function() {
  const workflowInfoBtn = document.getElementById('workflow-info');
  if (workflowInfoBtn) {
    workflowInfoBtn.addEventListener('click', function() {
      showWorkflowInfoModal();
    });
  }
});

// Workflow Info Modal
function showWorkflowInfoModal() {
  // Create modal content
  const content = `
    <div class="mb-4">
      <h4 class="mb-3">Smart Contract Automation Workflow</h4>
      <p>The EcoChain Guardian platform automates the entire lifecycle of sustainability reward contracts using blockchain technology. Here's how it works:</p>
    </div>
    
    <div class="mb-4">
      <h5><i class="fas fa-file-contract text-primary"></i> 1. Contract Deployment</h5>
      <p>Smart contracts are deployed using predefined templates optimized for different reward structures. These contracts are deployed to multiple blockchain networks including Ethereum, Polygon, and others to ensure optimal gas efficiency.</p>
    </div>
    
    <div class="mb-4">
      <h5><i class="fas fa-tasks text-primary"></i> 2. Score Integration</h5>
      <p>Sustainability scores from the scoring system are automatically fed into the smart contracts. These scores determine eligibility and reward amounts for mining operations. The integration happens through secure oracle networks to ensure data integrity.</p>
    </div>
    
    <div class="mb-4">
      <h5><i class="fas fa-calendar-check text-primary"></i> 3. Distribution Scheduling</h5>
      <p>Reward distributions can be scheduled as one-time events or recurring distributions. The system supports various distribution criteria including proportional to sustainability scores, equal distribution, or weighted by mining power.</p>
    </div>
    
    <div class="mb-4">
      <h5><i class="fas fa-coins text-primary"></i> 4. Reward Distribution</h5>
      <p>On the scheduled date, rewards are automatically distributed to qualifying mining operations. The distribution is executed on-chain, ensuring transparency and immutability. All transactions are recorded and can be verified on the blockchain.</p>
    </div>
    
    <div class="alert alert-info">
      <strong>Security Features:</strong> All contract deployments and distributions require multi-signature approval, ensuring that no single party can control the funds. Zero-knowledge proofs are used to verify sustainability claims without revealing sensitive operational data.
    </div>
  `;
  
  // Create and open modal
  const modalId = ModalSystem.create({
    title: 'Smart Contract Automation',
    content: content,
    size: 'large',
    buttons: [
      {
        text: 'View Documentation',
        class: 'btn-secondary',
        callback: () => {
          alert('In a real app, this would link to detailed documentation');
        }
      },
      {
        text: 'Close',
        class: 'btn-outline',
        action: 'close'
      }
    ]
  });
  
  ModalSystem.open(modalId);
}

// Replace the existing placeholder functions with our modal functions
window.viewContractDetails = showContractDetails;
window.viewTransactionDetails = showTransactionDetails;
window.viewProofDetails = showProofDetails;
window.viewOperationDetails = function(id) {
  alert(`Viewing details for operation ID: ${id}\nThis feature would show detailed metrics and history.`);
};
window.viewReport = function(id) {
  alert(`Viewing report: ${id}\nThis feature would display the full ESG report.`);
};

// Add new modal functions to window
window.showDeployContractModal = showDeployContractModal;
window.showScheduleDistributionModal = showScheduleDistributionModal; 