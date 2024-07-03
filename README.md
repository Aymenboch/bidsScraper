# Insightful Bids 

Insightful Bids is a dynamic web application designed to automate and streamline the process of extracting, analyzing, and visualizing data from various online sources. Utilizing a React front-end for a responsive user interface, the application integrates with a Flask-based API to handle server-side operations, while Scrapy is used for efficient data scraping.

## Key Features

- **Customizable Data Extraction**: Configure what data to scrape based on your needs.
- **Real-time Analytics Dashboard**: Visualize scraped data through interactive charts and graphs in real-time.
- **User-driven Query Capabilities**: Users can specify and modify the data they want to analyze through a user-friendly interface.

## Technology Stack

- **Frontend**: React
- **Backend**: Flask
- **Data Scraping**: Scrapy

## Getting Started

These instructions will guide you through getting a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You will need to install the following software:

- **Node.js**: Download and install from [Node.js official website](https://nodejs.org/)
- **Python**: Download and install from [Python.org](https://python.org/)
- **pip**: Usually comes with Python installation

### Installation

1. **Clone the repository**
   ```bash
   git clone https://yourrepositoryurl.git
   cd yourrepositoryname
2. **Set up the Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Mac/Linux
   .\venv\Scripts\activate   # On Windows
3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
4. **Install Node dependencies**
   ```bash
   cd bids
   npm install
5. **Start the backend server**
   ```bash
   cd ../flask
   python app.py
6. **Run the React application**
    ```bash
   cd ../bids
   npm start




