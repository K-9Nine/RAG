#!/bin/bash

# Update system
apt update && apt upgrade -y

# Install UFW if not present
apt install -y ufw

# Configure UFW
ufw default deny incoming
ufw default allow outgoing

# Allow SSH
ufw allow ssh

# Allow HTTP/HTTPS
ufw allow 8000/tcp  # FastAPI
ufw allow 8080/tcp  # Weaviate

# Enable UFW
ufw --force enable 