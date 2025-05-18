# RAG-based Restaurant Chatbot

A Retrieval Augmented Generation (RAG) based chatbot that answers user questions about restaurants using data scraped from restaurant websites.

## Project Overview

This project consists of the following components:

1. **Web Scraper**: Collects restaurant data including menus, locations, operating hours, etc.
2. **Knowledge Base**: Processes and stores scraped data for efficient retrieval
3. **RAG Chatbot**: Uses Hugging Face models to retrieve and generate responses
4. **User Interface**: Streamlit app for interacting with the chatbot

## Setup Instructions

### Prerequisites

- Python 3.8+
- Git

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/zomato-rag-chatbot.git
   cd zomato-rag-chatbot
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running the Web Scraper

To collect restaurant data:
```
python src/scraper/main.py
```

This will scrape data from the configured restaurant websites and save it to `data/raw/`.

### Building the Knowledge Base

To process the scraped data and build the knowledge base:
```
python src/knowledge_base/build_kb.py
```

This will process the raw data and create a structured knowledge base in `data/processed/`.

### Running the Chatbot Interface

To launch the Streamlit interface:
```
streamlit run src/app.py
```

Then open your browser and navigate to `http://localhost:8501` to interact with the chatbot.

## Project Structure

```
zomato-rag-chatbot/
├── data/                      # Data directory
│   ├── raw/                   # Raw scraped data
│   └── processed/             # Processed data for knowledge base
├── src/                       # Source code
│   ├── scraper/               # Web scraping module
│   ├── knowledge_base/        # Knowledge base processing
│   ├── rag/                   # RAG implementation
│   ├── utils/                 # Utility functions
│   └── app.py                 # Streamlit application
├── notebooks/                 # Jupyter notebooks for exploration
├── tests/                     # Test files
├── README.md                  # Project documentation
└── requirements.txt           # Package dependencies
```

## Features

- Scrapes data from multiple restaurant websites
- Structured knowledge base for efficient retrieval
- Natural language query processing
- Conversational interface via Streamlit
- Handles various types of restaurant-related queries
- Remembers conversation context

## Limitations

- Only works with data from scraped restaurants
- May not handle highly complex or ambiguous queries
- Limited to text-based information (no image processing)

## Future Improvements

- Expand the number of restaurants in the database
- Implement more advanced retrieval mechanisms
- Add sentiment analysis for restaurant reviews
- Improve handling of ambiguous queries
- Create a mobile application interface 
