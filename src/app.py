"""
Streamlit App for Restaurant Chatbot

This script creates a web-based user interface for the RAG restaurant chatbot
using Streamlit.
"""

import os
import sys
import streamlit as st
from pathlib import Path
import time

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.rag_chatbot import RAGChatbot
from utils.utils import get_restaurant_names, get_dietary_options

# Set page configuration
st.set_page_config(
    page_title="Restaurant Chatbot",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define function to initialize the chatbot
@st.cache_resource
def initialize_chatbot():
    # Set up the chatbot
    kb_dir = "data/processed/kb"
    generator_model = "google/flan-t5-base"
    
    # Check if knowledge base exists
    if not os.path.exists(kb_dir):
        st.warning("Knowledge base not found. Please run the scraper and build the knowledge base first.")
        return None
    
    try:
        # Initialize the chatbot
        return RAGChatbot(
            knowledge_base_dir=kb_dir,
            generator_model=generator_model
        )
    except Exception as e:
        st.error(f"Error initializing chatbot: {str(e)}")
        return None

# Apply custom CSS
def apply_custom_css():
    st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: row;
        align-items: flex-start;
    }
    .chat-message.user {
        background-color: #DCF8C6;
    }
    .chat-message.bot {
        background-color: #f0f0f0;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .chat-message .message {
        flex-grow: 1;
    }
    .stButton button {
        width: 100%;
        border-radius: 20px;
        font-size: 1rem;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }
    h1, h2, h3 {
        color: #FF5733;
    }
    .restaurant-card {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Display chat messages
def display_chat_messages():
    if "messages" in st.session_state:
        for message in st.session_state.messages:
            if message["role"] == "user":
                display_user_message(message["content"])
            else:
                display_assistant_message(message["content"])

# Display user message
def display_user_message(message):
    st.markdown(f"""
    <div class="chat-message user">
        <img class="avatar" src="https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y">
        <div class="message">{message}</div>
    </div>
    """, unsafe_allow_html=True)

# Display assistant message
def display_assistant_message(message):
    st.markdown(f"""
    <div class="chat-message bot">
        <img class="avatar" src="https://api.dicebear.com/7.x/bottts/svg?seed=Coco">
        <div class="message">{message}</div>
    </div>
    """, unsafe_allow_html=True)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main function
def main():
    apply_custom_css()
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4080/4080032.png", width=100)
        st.title("Restaurant Chatbot")
        st.markdown("---")
        
        st.subheader("About")
        st.write(
            "This chatbot uses Retrieval Augmented Generation (RAG) to answer "
            "your questions about restaurants and their menus."
        )
        
        st.markdown("---")
        
        # Example queries
        st.subheader("Example Queries")
        example_queries = [
            "Which restaurant has vegetarian options?",
            "Tell me about Italian Restaurant's menu",
            "Compare the prices between Burger Joint and Taco Haven",
            "Does Sushi Express have any gluten-free items?",
            "What's the price range for Mediterranean Delight's dessert menu?"
        ]
        
        for query in example_queries:
            if st.button(query):
                st.session_state.user_input = query
                
        st.markdown("---")
        
        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.messages = []
            if "chatbot" in st.session_state and st.session_state.chatbot:
                st.session_state.chatbot.clear_chat_history()
            st.rerun()
    
    # Main content
    st.title("🍽️ Restaurant Information Assistant")
    st.markdown(
        "Welcome! I can answer questions about restaurants, their menus, "
        "dietary options, and more. How can I help you today?"
    )
    
    # Initialize or get the chatbot
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = initialize_chatbot()
    
    chatbot = st.session_state.chatbot
    
    # Check if chatbot initialized successfully
    if not chatbot:
        st.error("Chatbot could not be initialized. Please check the knowledge base.")
        return
    
    # Display chat messages
    display_chat_messages()
    
    # Chat input
    user_input = st.chat_input("Ask me about restaurants...")
    
    # Handle user input
    if user_input:
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        display_user_message(user_input)
        
        with st.spinner("Thinking..."):
            # Get chatbot response
            try:
                response = chatbot.answer(user_input)
                
                # Add assistant message to session state
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Display assistant message
                display_assistant_message(response)
            except Exception as e:
                st.error(f"Error getting response: {str(e)}")
    
    # Restaurant directory section
    st.markdown("---")
    with st.expander("🏙️ Restaurant Directory", expanded=False):
        st.markdown("Here are all the restaurants in our database:")
        
        restaurant_names = get_restaurant_names()
        if restaurant_names:
            cols = st.columns(3)
            for i, name in enumerate(restaurant_names):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="restaurant-card">
                        <h3>{name}</h3>
                        <p>Click to ask about this restaurant:</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Tell me about {name}", key=f"btn_{name}"):
                        query = f"Tell me about {name}'s menu and location"
                        st.session_state.messages.append({"role": "user", "content": query})
                        
                        with st.spinner("Thinking..."):
                            response = chatbot.answer(query)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        
                        st.rerun()
        else:
            st.write("No restaurants found in the database.")
    
    # Dietary preferences section
    with st.expander("🥗 Dietary Preferences Guide", expanded=False):
        st.markdown("We can help you find menu items for these dietary preferences:")
        
        dietary_options = get_dietary_options()
        diet_cols = st.columns(len(dietary_options))
        
        for i, diet in enumerate(dietary_options):
            with diet_cols[i]:
                if st.button(diet.capitalize(), key=f"diet_{diet}"):
                    query = f"Which restaurants have {diet} options on their menu?"
                    st.session_state.messages.append({"role": "user", "content": query})
                    
                    with st.spinner("Thinking..."):
                        response = chatbot.answer(query)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    st.rerun()

if __name__ == "__main__":
    main() 