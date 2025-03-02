# components/ai_engine.py
import streamlit as st
import json
import requests
from typing import Dict, Any, List, Optional

class OllamaEngine:
    """Component for interacting with Ollama API for AI processing."""
    
    def __init__(self):
        """Initialize the Ollama API engine."""
        # Default URL for local Ollama instance
        self.api_url = st.sidebar.text_input(
            "Ollama API URL",
            value="http://localhost:11434/api/generate",
            help="URL of the Ollama API endpoint"
        )
        
        # Model selection
        self.model = st.sidebar.selectbox(
            "Select Ollama Model",
            ["llama3", "llama2", "mistral", "gemma", "phi", "custom"],
            help="Choose the LLM model to use"
        )
        
        # Custom model input
        if self.model == "custom":
            self.model = st.sidebar.text_input("Enter Custom Model Name")
        
        # Advanced parameters
        with st.sidebar.expander("Advanced Parameters"):
            self.temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
            self.max_tokens = st.slider("Max Tokens", 100, 4000, 1000, 100)
    
    def generate_prompt(self, df, query: str) -> str:
        """Generate a prompt for Ollama based on the dataframe and query."""
        # Get dataframe info
        columns_info = {
            col: str(df[col].dtype) for col in df.columns
        }
        
        sample_data = df.head(5).to_dict()
        
        # Create a detailed prompt with context
        prompt = f"""
        I have a CSV dataset with the following columns and data types:
        {json.dumps(columns_info, indent=2)}
        
        Here's a sample of the data:
        {json.dumps(sample_data, indent=2)}
        
        The dataset has {df.shape[0]} rows and {df.shape[1]} columns.
        
        Based on this information, please answer the following question:
        {query}
        
        Provide a detailed analysis using the data provided. If there's insufficient data to answer the question, please indicate what additional information would be needed.
        """
        
        return prompt.strip()
    
    def query(self, df, query: str) -> str:
        """Send a query to Ollama API and return the response."""
        try:
            prompt = self.generate_prompt(df, query)
            
            # Prepare the payload for the API request
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False
            }
            
            with st.spinner("Processing query with Ollama..."):
                # Make the API request
                response = requests.post(self.api_url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "No response generated")
                else:
                    st.error(f"Error from Ollama API: {response.status_code}")
                    st.error(response.text)
                    return f"Error: Unable to get response from Ollama API (Status code: {response.status_code})"
        
        except Exception as e:
            st.error(f"Error querying Ollama: {str(e)}")
            return f"Error: {str(e)}"