// EcoChain Guardian - Interactive Features

document.addEventListener('DOMContentLoaded', function() {
    // Add animation classes to elements when they come into view
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.feature-card, .screenshot, .stat-item, .section-title');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight - 100) {
                element.classList.add('animate-fade-in');
            }
        });
    };
    
    // Run once on page load
    animateOnScroll();
    
    // Run on scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Navbar color change on scroll
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const navbarHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - navbarHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add dark mode toggle
    const body = document.body;
    const darkModeToggle = document.createElement('div');
    darkModeToggle.className = 'dark-mode-toggle';
    darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    body.appendChild(darkModeToggle);
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
        darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    // Toggle dark mode
    darkModeToggle.addEventListener('click', function() {
        body.classList.toggle('dark-mode');
        
        if (body.classList.contains('dark-mode')) {
            localStorage.setItem('theme', 'dark');
            darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            localStorage.setItem('theme', 'light');
            darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
    });
    
    // Add interactive demo tabs
    const demoTabs = document.querySelectorAll('.demo-tab');
    const demoContents = document.querySelectorAll('.demo-content');
    
    if (demoTabs.length > 0 && demoContents.length > 0) {
        demoTabs.forEach((tab, index) => {
            tab.addEventListener('click', function() {
                // Remove active class from all tabs and contents
                demoTabs.forEach(t => t.classList.remove('active'));
                demoContents.forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding content
                tab.classList.add('active');
                demoContents[index].classList.add('active');
            });
        });
        
        // Activate first tab by default
        demoTabs[0].click();
    }
    
    // Add interactive comparison slider
    const comparisonSlider = document.querySelector('.comparison-slider');
    if (comparisonSlider) {
        const slider = comparisonSlider.querySelector('.slider');
        const beforeImage = comparisonSlider.querySelector('.before-image');
        
        slider.addEventListener('input', function() {
            const sliderValue = this.value;
            beforeImage.style.width = `${sliderValue}%`;
        });
    }
    
    // Add counter animation for stats
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const animateCounter = (element, target) => {
        const duration = 2000; // 2 seconds
        const startTime = performance.now();
        const startValue = 0;
        
        const updateCounter = (currentTime) => {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1);
            
            // Easing function for smoother animation
            const easeOutQuad = progress * (2 - progress);
            
            let currentValue;
            if (target.toString().includes('x')) {
                // Handle values with 'x' suffix (like 300x)
                const numericTarget = parseFloat(target);
                currentValue = Math.floor(startValue + (numericTarget - startValue) * easeOutQuad);
                element.textContent = `${currentValue}x`;
            } else if (target.toString().includes('%')) {
                // Handle percentage values
                const numericTarget = parseFloat(target);
                currentValue = Math.floor(startValue + (numericTarget - startValue) * easeOutQuad);
                element.textContent = `${currentValue}%`;
            } else {
                // Handle regular numeric values
                currentValue = Math.floor(startValue + (target - startValue) * easeOutQuad);
                element.textContent = currentValue;
            }
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        };
        
        requestAnimationFrame(updateCounter);
    };
    
    // Observer for stats section
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                statNumbers.forEach(stat => {
                    const targetValue = stat.textContent;
                    stat.textContent = '0';
                    animateCounter(stat, targetValue);
                });
                statsObserver.disconnect();
            }
        });
    }, { threshold: 0.5 });
    
    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        statsObserver.observe(statsSection);
    }
    
    // Add typed effect to hero heading
    const heroHeading = document.querySelector('.hero h1');
    if (heroHeading) {
        const originalText = heroHeading.textContent;
        heroHeading.textContent = '';
        
        let i = 0;
        const typeEffect = () => {
            if (i < originalText.length) {
                heroHeading.textContent += originalText.charAt(i);
                i++;
                setTimeout(typeEffect, 50);
            }
        };
        
        setTimeout(typeEffect, 500);
    }

    // NEW CODE FOR INTERACTIVE MODEL TESTING

    // Sustainability Scoring Model
    const sustainabilityForm = document.getElementById('sustainabilityForm');
    if (sustainabilityForm) {
        sustainabilityForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form values
            const energySource = document.getElementById('energySource').value;
            const energyConsumption = parseInt(document.getElementById('energyConsumption').value);
            const hashRate = parseInt(document.getElementById('hashRate').value);
            const location = document.getElementById('location').value;
            const coolingSystem = document.getElementById('coolingSystem').value;
            const carbonOffset = parseInt(document.getElementById('carbonOffset').value);
            
            // Calculate scores (this is a simplified model for demo purposes)
            const energySourceScores = {
                'solar': 95,
                'wind': 90,
                'hydro': 85,
                'geothermal': 80,
                'natural_gas': 40,
                'coal': 10,
                'mixed': 50
            };
            
            const locationFactors = {
                'north_america': 0.9,
                'europe': 1.0,
                'asia': 0.8,
                'south_america': 0.85,
                'africa': 0.75,
                'oceania': 0.95
            };
            
            const coolingFactors = {
                'air': 0.7,
                'liquid': 0.85,
                'immersion': 0.95,
                'geothermal': 1.0
            };
            
            // Calculate efficiency score (hash rate per energy consumption)
            const efficiencyRaw = (hashRate / energyConsumption) * 1000;
            const efficiencyScore = Math.min(Math.round(efficiencyRaw * 50), 100);
            
            // Calculate carbon score
            const baseCarbon = energySourceScores[energySource] || 50;
            const carbonScore = Math.min(Math.round(baseCarbon * (1 + carbonOffset / 100)), 100);
            
            // Calculate renewable score
            const renewableScore = energySourceScores[energySource] || 50;
            
            // Calculate overall score
            const locationFactor = locationFactors[location] || 0.85;
            const coolingFactor = coolingFactors[coolingSystem] || 0.8;
            
            const overallScore = Math.round(
                (efficiencyScore * 0.4 + carbonScore * 0.4 + renewableScore * 0.2) * 
                locationFactor * coolingFactor
            );
            
            // Update the UI
            const resultContainer = document.getElementById('sustainabilityResult');
            resultContainer.classList.remove('d-none');
            
            // Update gauge
            const gaugeFill = document.querySelector('.gauge-fill');
            const gaugeValue = document.querySelector('.gauge-value');
            const rotateDegrees = (overallScore / 100) * 180;
            gaugeFill.style.transform = `rotate(${rotateDegrees}deg)`;
            
            // Animate the gauge value
            let currentValue = 0;
            const gaugeInterval = setInterval(() => {
                currentValue++;
                gaugeValue.textContent = currentValue;
                if (currentValue >= overallScore) {
                    clearInterval(gaugeInterval);
                }
            }, 20);
            
            // Update progress bars
            document.getElementById('efficiencyScore').textContent = `${efficiencyScore}/100`;
            document.getElementById('efficiencyBar').style.width = `${efficiencyScore}%`;
            document.getElementById('efficiencyBar').className = `progress-bar ${efficiencyScore > 70 ? 'bg-success' : efficiencyScore > 40 ? 'bg-warning' : 'bg-danger'}`;
            
            document.getElementById('carbonScore').textContent = `${carbonScore}/100`;
            document.getElementById('carbonBar').style.width = `${carbonScore}%`;
            document.getElementById('carbonBar').className = `progress-bar ${carbonScore > 70 ? 'bg-success' : carbonScore > 40 ? 'bg-warning' : 'bg-danger'}`;
            
            document.getElementById('renewableScore').textContent = `${renewableScore}/100`;
            document.getElementById('renewableBar').style.width = `${renewableScore}%`;
            document.getElementById('renewableBar').className = `progress-bar ${renewableScore > 70 ? 'bg-success' : renewableScore > 40 ? 'bg-warning' : 'bg-danger'}`;
            
            // Update feedback
            const feedback = document.getElementById('sustainabilityFeedback');
            if (overallScore > 80) {
                feedback.className = 'alert alert-success mt-3';
                feedback.innerHTML = '<i class="fas fa-award me-2"></i> Excellent! This operation qualifies for premium EcoToken rewards.';
            } else if (overallScore > 60) {
                feedback.className = 'alert alert-info mt-3';
                feedback.innerHTML = '<i class="fas fa-thumbs-up me-2"></i> Good sustainability score. Standard EcoToken rewards apply.';
            } else if (overallScore > 40) {
                feedback.className = 'alert alert-warning mt-3';
                feedback.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i> Moderate sustainability. Consider upgrading to renewable energy sources.';
            } else {
                feedback.className = 'alert alert-danger mt-3';
                feedback.innerHTML = '<i class="fas fa-times-circle me-2"></i> Poor sustainability score. Significant improvements needed to qualify for rewards.';
            }
        });
    }
    
    // Anomaly Detection Model
    const anomalyDataSelect = document.getElementById('anomalyDataSelect');
    const detectAnomaliesBtn = document.getElementById('detectAnomalies');
    
    if (anomalyDataSelect && detectAnomaliesBtn) {
        // Sample data for demo purposes
        const sampleData = {
            'sample1': {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                values: [45, 47, 46, 48, 49, 47, 48, 46, 45, 47, 48, 46],
                anomalies: []
            },
            'sample2': {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                values: [45, 47, 46, 48, 22, 47, 48, 46, 45, 15, 48, 46],
                anomalies: [4, 9]
            },
            'sample3': {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                values: [45, 47, 46, 48, 49, 47, 35, 46, 45, 47, 60, 46],
                anomalies: [6, 10]
            }
        };
        
        // Clear file input when sample is selected
        anomalyDataSelect.addEventListener('change', function() {
            document.getElementById('anomalyData').value = '';
        });
        
        // Clear sample selection when file is selected
        document.getElementById('anomalyData').addEventListener('change', function() {
            anomalyDataSelect.value = '';
        });
        
        // Clear file button
        document.getElementById('clearAnomalyFile').addEventListener('click', function() {
            document.getElementById('anomalyData').value = '';
        });
        
        // Detect anomalies button
        detectAnomaliesBtn.addEventListener('click', function() {
            const selectedSample = anomalyDataSelect.value;
            const fileInput = document.getElementById('anomalyData');
            
            // For demo purposes, we'll only use the sample data
            if (!selectedSample && !fileInput.files.length) {
                alert('Please select a sample or upload a file');
                return;
            }
            
            // Get the result container
            const resultContainer = document.getElementById('anomalyResult');
            resultContainer.classList.remove('d-none');
            
            // Show loading state
            resultContainer.innerHTML = `
                <div class="text-center my-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3">Analyzing data for anomalies...</p>
                </div>
            `;
            
            // Simulate processing delay
            setTimeout(() => {
                // Use the selected sample data
                const data = sampleData[selectedSample];
                
                // Update the UI with results
                const totalPoints = data.labels.length;
                const anomaliesCount = data.anomalies.length;
                const confidenceScore = Math.round(90 - (anomaliesCount * 5));
                
                // Create chart
                const ctx = document.createElement('canvas');
                ctx.id = 'anomalyChart';
                
                // Replace loading spinner with chart
                resultContainer.innerHTML = `
                    <h5 class="mb-3">Anomaly Detection Results</h5>
                    <div class="chart-container" style="position: relative; height:300px; width:100%">
                    </div>
                    <div class="mt-4">
                        <h6>Analysis Summary</h6>
                        <ul class="list-group">
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                Total data points analyzed
                                <span class="badge bg-primary rounded-pill" id="totalDataPoints">${totalPoints}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                Anomalies detected
                                <span class="badge bg-danger rounded-pill" id="anomaliesCount">${anomaliesCount}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                Confidence score
                                <span class="badge bg-info rounded-pill" id="confidenceScore">${confidenceScore}%</span>
                            </li>
                        </ul>
                    </div>
                    <div class="alert ${anomaliesCount > 0 ? 'alert-warning' : 'alert-success'} mt-3" id="anomalyFeedback">
                        ${anomaliesCount > 0 ? 
                            `<i class="fas fa-exclamation-triangle me-2"></i> ${anomaliesCount} anomalies detected in the data. Further investigation recommended.` : 
                            '<i class="fas fa-check-circle me-2"></i> No anomalies detected. Data appears consistent.'}
                    </div>
                `;
                
                // Add chart to container
                const chartContainer = resultContainer.querySelector('.chart-container');
                chartContainer.appendChild(ctx);
                
                // Create chart using Chart.js (if available)
                if (window.Chart) {
                    new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: data.labels,
                            datasets: [{
                                label: 'Energy Efficiency (kWh/TH)',
                                data: data.values,
                                borderColor: 'rgba(46, 204, 113, 1)',
                                backgroundColor: 'rgba(46, 204, 113, 0.1)',
                                borderWidth: 2,
                                tension: 0.4,
                                fill: true
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            const index = context.dataIndex;
                                            let label = context.dataset.label || '';
                                            
                                            if (label) {
                                                label += ': ';
                                            }
                                            
                                            label += context.raw;
                                            
                                            if (data.anomalies.includes(index)) {
                                                label += ' (ANOMALY DETECTED)';
                                            }
                                            
                                            return label;
                                        }
                                    }
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: false,
                                    suggestedMin: Math.min(...data.values) * 0.8,
                                    suggestedMax: Math.max(...data.values) * 1.2
                                }
                            }
                        }
                    });
                } else {
                    // Fallback if Chart.js is not available
                    chartContainer.innerHTML = `
                        <div class="p-3 bg-light rounded">
                            <p class="text-center mb-0">Chart library not loaded. Please include Chart.js for visualization.</p>
                        </div>
                    `;
                }
            }, 1500);
        });
    }
    
    // zkSNARK Verification Demo
    const generateProofBtn = document.getElementById('generateProof');
    const verifyProofBtn = document.getElementById('verifyProof');
    
    if (generateProofBtn && verifyProofBtn) {
        generateProofBtn.addEventListener('click', function() {
            // Get form values
            const operationId = document.getElementById('operationId').value;
            const energyData = parseInt(document.getElementById('energyData').value);
            const carbonData = parseInt(document.getElementById('carbonData').value);
            const threshold = parseFloat(document.getElementById('sustainabilityThreshold').value);
            
            // Calculate carbon intensity (kg CO2 / kWh)
            const carbonIntensity = carbonData / energyData;
            
            // Generate a mock proof (in a real system, this would be a zkSNARK proof)
            const proofData = document.getElementById('proofData');
            const publicInputs = document.getElementById('publicInputs');
            
            // Show generating proof animation
            proofData.value = 'Generating proof...';
            
            setTimeout(() => {
                // Create a mock proof (base64-like string)
                const mockProof = btoa(JSON.stringify({
                    operationId,
                    threshold,
                    isBelowThreshold: carbonIntensity <= threshold,
                    timestamp: Date.now()
                })).substring(0, 100) + '...';
                
                proofData.value = mockProof;
                publicInputs.value = `Operation: ${operationId}, Threshold: ${threshold} kg CO2/kWh`;
                
                // Enable verify button
                verifyProofBtn.disabled = false;
            }, 1500);
        });
        
        verifyProofBtn.addEventListener('click', function() {
            const verificationResult = document.querySelector('.verification-result');
            const verificationSpinner = document.querySelector('.verification-spinner');
            const verificationSuccess = document.querySelector('.verification-success');
            const verificationFailure = document.querySelector('.verification-failure');
            
            // Get threshold and carbon data
            const threshold = parseFloat(document.getElementById('sustainabilityThreshold').value);
            const energyData = parseInt(document.getElementById('energyData').value);
            const carbonData = parseInt(document.getElementById('carbonData').value);
            
            // Calculate carbon intensity
            const carbonIntensity = carbonData / energyData;
            const isBelowThreshold = carbonIntensity <= threshold;
            
            // Show verification process
            verificationResult.classList.remove('d-none');
            verificationSpinner.classList.remove('d-none');
            verificationSuccess.classList.add('d-none');
            verificationFailure.classList.add('d-none');
            
            // Simulate verification delay
            setTimeout(() => {
                verificationSpinner.classList.add('d-none');
                
                if (isBelowThreshold) {
                    verificationSuccess.classList.remove('d-none');
                } else {
                    verificationFailure.classList.remove('d-none');
                }
            }, 2000);
        });
    }

    // Add Chart.js library dynamically
    const addChartJs = () => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        document.head.appendChild(script);
    };
    
    // Load Chart.js if the anomaly detection tab exists
    if (document.getElementById('anomaly-tab')) {
        addChartJs();
    }
}); 