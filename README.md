# PDF Sustainibility Analyzer for Projects

## Team Members

- Nathalie Kern
- Maria Näf
- Sophie Maier

## Overview

To improve the projectmanagement method regarding sustainability, the projectteam created a PDF analyzer with a Chat GPT API.

### Prerequisites

Following must be installed on your system:

- Python
- Git

### Setup

Here's how you can set up your development environment:

```bash
# Clone the repository
git clone https://github.com/sophiemaier/Open-Data-Hack-2023

# Navigate to the project directory
cd Open-Data-Hack-2023

# Create a Python virtual environment in the 'venv' directory
py -m venv venv

# Activate the virtual environment (use the correct command for your operating system)
venv\Scripts\activate # For Windows in Git Bash
# or
source venv/bin/activate # For Unix or Linux systems

# Install the project dependencies from 'requirements.txt'
pip install -r requirements.txt


# Create a API key from chat gpt on their website and replace "YOUR KEY" with your key. After that, create a '.env' file in the 'OpenDataHack2023' directory with the following content
echo OPENAI_API_KEY="YOUR KEY" >> .env



# Run the local development server or script (specify the script if it's not 'app.py')
streamlit run app.py
