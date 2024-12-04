# IT Support Assistant with RAG

An AI-powered IT support assistant that uses Retrieval-Augmented Generation (RAG) to provide context-aware responses based on your organization's support documentation.

## Features

- Chat interface for IT support queries
- Integration with OpenAI GPT models
- Document storage and retrieval using Weaviate
- Context-aware responses using RAG
- Support for VoIP, email, and other IT systems

## Prerequisites

- Python 3.8+
- Docker (for Weaviate)
- OpenAI API key

## Setup

1. Clone the repository: 

# Deployment Instructions

## Local Deployment

## Deployment to DigitalOcean

1. Create a Droplet:
   - Go to DigitalOcean dashboard
   - Click "Create" > "Droplets"
   - Choose:
     - Ubuntu 22.04 LTS
     - Basic Plan ($12/month is sufficient)
     - Choose datacenter region (e.g., London)
     - Select "Docker" from Marketplace

2. Access Your Droplet:
   ```bash
   ssh root@your-droplet-ip
   ```

3. Clone and Setup:
   ```bash
   # Clone repository
   git clone https://github.com/YourUsername/RAG.git
   cd RAG

   # Create .env file
   cp .env.template .env
   nano .env  # Add your OpenAI API key
   ```

4. Start Services:
   ```bash
   # Build and start containers
   docker-compose up -d

   # Load documents
   docker-compose exec app python src/utils/load_test_docs.py
   ```

5. Access the Chat Interface:
   - Open http://your-droplet-ip:8000 in a browser
   - Share this URL with your colleagues

## Maintenance

- View logs:
  ```bash
  docker-compose logs -f
  ```

- Update documents:
  ```bash
  docker-compose exec app python src/utils/load_test_docs.py
  ```

- Restart services:
  ```bash
  docker-compose restart
  ```
