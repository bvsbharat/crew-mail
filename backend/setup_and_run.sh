#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Install missing dependencies
pip install langchain-community

# Try to run the application
cd src
python -m email_auto_responder_flow.main