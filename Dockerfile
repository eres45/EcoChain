FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the package code
COPY . .

# Install the package
RUN pip install -e .

# Create directories
RUN mkdir -p /app/config /app/data

# Run a basic check that the package is installed correctly
RUN python -c "from ecochain.agent_module.eco_agent import EcoAgent; print('Package installed successfully')"

# Set command
CMD ["ecochain", "run"] 