# Zomato RAG-based Restaurant Chatbot - Documentation

This document provides detailed information about the system architecture, implementation details, design decisions, challenges faced, and future improvement opportunities for the restaurant data scraper and RAG chatbot project.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Implementation Details](#implementation-details)
   - [Web Scraper](#web-scraper)
   - [Knowledge Base](#knowledge-base)
   - [RAG Chatbot](#rag-chatbot)
   - [User Interface](#user-interface)
3. [Design Decisions](#design-decisions)
4. [Challenges and Solutions](#challenges-and-solutions)
5. [Future Improvements](#future-improvements)
6. [Usage Guide](#usage-guide)

## System Architecture

The Restaurant Chatbot system consists of the following components that work together to provide a seamless user experience:

1. **Web Scraper**: Collects data from restaurant websites, including menus, locations, hours, and special features.
2. **Knowledge Base**: Processes and structures the scraped data for efficient retrieval.
3. **RAG Chatbot**: Combines retrieval and generation to answer user queries.
   - **Retriever**: Finds relevant information from the knowledge base.
   - **Generator**: Generates natural language responses based on retrieved information.
4. **User Interface**: Streamlit web app for interacting with the chatbot.

The system follows a pipeline approach:
1. Data is collected via web scraping
2. Raw data is processed and transformed into a structured format
3. A knowledge base is created with vector embeddings for efficient retrieval
4. The RAG chatbot uses the knowledge base to answer user queries
5. Users interact with the system through a web interface

## Implementation Details

### Web Scraper

The web scraper module is designed to collect data from restaurant websites and store it in a structured format. It uses BeautifulSoup for HTML parsing and implements the following features:

- **Flexible Configuration**: Each restaurant has a custom configuration specifying CSS selectors for extracting data.
- **Robust Error Handling**: The scraper handles network errors, missing elements, and other issues gracefully.
- **Rate Limiting**: Random delays between requests to avoid overwhelming websites.
- **Data Extraction**: Extracts restaurant names, locations, menu items, prices, descriptions, dietary information, operating hours, and special features.
- **Mock Data Generation**: For testing purposes, the scraper can generate mock data without actually scraping websites.

Key files:
- `src/scraper/restaurant_scraper.py`: Main scraper class
- `src/scraper/restaurant_configs.py`: Restaurant-specific configurations
- `src/scraper/main.py`: Entry point for running the scraper

### Knowledge Base

The knowledge base module processes the raw scraped data and transforms it into a format suitable for efficient retrieval. It includes:

- **Data Cleaning**: Normalizes text, removes duplicates, and handles missing values.
- **Data Structuring**: Organizes data into a consistent format across different restaurants.
- **Vector Embeddings**: Creates embeddings for restaurant and menu item information.
- **Indexing**: Uses FAISS to create an efficient vector index for similarity search.

Key files:
- `src/knowledge_base/data_processor.py`: Processes raw data
- `src/knowledge_base/build_kb.py`: Builds the knowledge base with embeddings and index

### RAG Chatbot

The RAG (Retrieval Augmented Generation) chatbot combines retrieval and generation techniques to provide accurate responses to user queries. It includes:

- **Document Retriever**: Retrieves relevant documents from the knowledge base based on semantic similarity.
- **Response Generator**: Generates natural language responses using a language model.
- **Conversation Management**: Keeps track of conversation history for contextual responses.
- **Intent Detection**: Analyzes user queries to determine the appropriate retrieval strategy.

Key files:
- `src/rag/retriever.py`: Handles document retrieval
- `src/rag/generator.py`: Generates responses from retrieved documents
- `src/rag/rag_chatbot.py`: Combines retriever and generator

### User Interface

The user interface is implemented as a Streamlit web application that provides an intuitive way for users to interact with the chatbot. It includes:

- **Chat Interface**: Displays the conversation history and allows users to input queries.
- **Restaurant Directory**: Shows all restaurants in the database and allows quick queries about them.
- **Dietary Preferences Guide**: Provides shortcuts for querying about specific dietary options.
- **Example Queries**: Suggests example queries to help users get started.

Key files:
- `src/app.py`: Streamlit application

## Design Decisions

Several key design decisions were made to optimize the system's performance, maintainability, and user experience:

1. **Modular Architecture**: The system is divided into independent modules that can be developed, tested, and maintained separately.

2. **Vector Search with FAISS**: We chose FAISS for similarity search because it provides efficient, scalable retrieval of vector embeddings.

3. **Sentence Transformers**: We use sentence-transformers models for creating embeddings because they provide high-quality semantic representations with reasonable computational requirements.

4. **Two-Stage RAG**: The system first retrieves relevant documents and then generates responses based on those documents, which provides better accuracy and control over the output.

5. **Intent Detection**: By analyzing the query type, we can apply specialized retrieval strategies for different types of questions (menu items, dietary preferences, restaurant information, comparisons).

6. **Mock Data Support**: For development and testing, the system can generate and use mock data instead of actually scraping websites.

7. **Streamlit for UI**: Streamlit provides a simple, efficient way to create interactive web applications without complex frontend development.

## Challenges and Solutions

During the development of this system, several challenges were encountered and addressed:

1. **Website Structure Variability**: Different restaurant websites have different structures, making it difficult to create a one-size-fits-all scraper.
   - Solution: Created a flexible configuration system that can be customized for each restaurant.

2. **Handling Missing or Inconsistent Data**: Restaurants often present information in inconsistent formats.
   - Solution: Implemented robust data cleaning and normalization routines.

3. **Semantic Search Accuracy**: Simple keyword matching isn't sufficient for understanding user queries.
   - Solution: Used sentence transformer models to create semantic embeddings for better matching.

4. **Balancing Response Detail and Brevity**: Responses need to be informative but not overwhelming.
   - Solution: Structured prompts carefully to guide the LLM in generating concise, relevant responses.

5. **Resource Constraints**: Large language models can be resource-intensive.
   - Solution: Used smaller, more efficient models (flan-t5-base) and optimized the retrieval process.

## Future Improvements

There are several opportunities for enhancing the system in the future:

1. **Multi-modal Support**: Add capability to handle images of food items, restaurant interiors, etc.

2. **User Preference Learning**: Track user preferences and provide personalized recommendations.

3. **Real-time Data Updates**: Implement a scheduled scraping system to keep the data up-to-date.

4. **Expanded Restaurant Coverage**: Scale up the system to cover hundreds or thousands of restaurants.

5. **Advanced NLP Features**:
   - Sentiment analysis of reviews
   - More sophisticated query understanding
   - Multi-turn conversation capabilities

6. **Performance Optimization**:
   - Caching common queries
   - Distributed retrieval for larger knowledge bases
   - Model quantization for faster inference

7. **Mobile App Interface**: Develop a mobile application for easier access.

## Usage Guide

### Running the Scraper

To collect restaurant data:

```bash
python run.py scrape [--restaurant RESTAURANT_NAME] [--mock]
```

Options:
- `--restaurant`: Scrape a specific restaurant (optional)
- `--mock`: Use mock data instead of scraping real websites (for testing)

### Building the Knowledge Base

To process the scraped data and build the knowledge base:

```bash
python run.py build_kb [--process] [--model MODEL_NAME]
```

Options:
- `--process`: Process raw data before building the knowledge base
- `--model`: Specify a different sentence transformer model (default: sentence-transformers/all-MiniLM-L6-v2)

### Running the Chatbot Interface

To start the Streamlit application:

```bash
python run.py app
```

### Running the Complete Pipeline

To run all steps (scrape, build knowledge base, and run app):

```bash
python run.py pipeline [--restaurant RESTAURANT_NAME] [--mock] [--model MODEL_NAME]
```

### Example Queries

The chatbot can handle various types of queries, including:

1. **Menu Information**:
   - "What items are on Italian Restaurant's menu?"
   - "Does Burger Joint have vegetarian options?"
   - "What's the price range for Mediterranean Delight's dessert menu?"

2. **Restaurant Features**:
   - "Which restaurants have outdoor seating?"
   - "Tell me about Sushi Express's location and hours."
   - "What are the special features of Taco Haven?"

3. **Dietary Preferences**:
   - "Which restaurant has the best options for vegans?"
   - "Are there gluten-free appetizers at Golden Dragon?"
   - "Show me dairy-free dessert options at Pizzeria Napoli."

4. **Comparisons**:
   - "Compare the spicy dishes at Spice Garden and Thai Palace."
   - "What's the difference between Burger Joint and Taco Haven's price range?"
   - "Which restaurant between Italian Restaurant and Mediterranean Delight has more vegetarian options?" 