# components/query_interface.py
import streamlit as st
import pandas as pd
from components.ai_engine import OllamaEngine

class QueryInterface:
    """Component for processing natural language queries about the data."""
    
    def __init__(self, ai_engine):
        """Initialize the query interface with the AI engine."""
        self.ai_engine = ai_engine
        self.history = []
    
    def process_query(self, df):
        """Process a natural language query about the data."""
        # Query input
        query = st.text_area("Enter your question about the data", height=100)
        
        # Example queries to help users
        with st.expander("Example Queries"):
            examples = [
                "What are the main trends in this dataset?",
                "Summarize the key statistics for column X",
                "What's the correlation between column X and Y?",
                "Are there any outliers in the dataset?",
                "What insights can you derive from this data?",
                "How does X compare to Y across different categories?",
                "What recommendations would you make based on this data?"
            ]
            for i, example in enumerate(examples):
                if st.button(f"Example {i+1}", key=f"example_{i}"):
                    query = example
                    st.session_state.query = example
        
        # Process query
        if query:
            with st.spinner("Processing..."):
                response = self.ai_engine.query(df, query)
                
                # Add to history
                self.history.append({"query": query, "response": response})
                
                # Display response
                st.subheader("Response")
                st.markdown(response)
                
                # Offer to run code if response contains Python code
                if "```python" in response:
                    if st.button("Run Code Snippet"):
                        try:
                            # Extract code between triple backticks
                            code_blocks = []
                            lines = response.split("\n")
                            collecting = False
                            current_block = []
                            
                            for line in lines:
                                if line.strip() == "```python" or line.strip() == "```":
                                    if collecting:
                                        code_blocks.append("\n".join(current_block))
                                        current_block = []
                                    collecting = not collecting
                                elif collecting:
                                    current_block.append(line)
                            
                            # Execute code blocks
                            for i, code in enumerate(code_blocks):
                                with st.expander(f"Code Execution Result {i+1}"):
                                    st.code(code, language="python")
                                    # Create a local context with df available
                                    local_vars = {"df": df, "pd": pd}
                                    # Execute the code
                                    exec(code, globals(), local_vars)
                                    # Extract and display any figures created
                                    if "plt" in code:
                                        st.pyplot(plt.gcf())
                                        plt.clf()
                        except Exception as e:
                            st.error(f"Error executing code: {str(e)}")
        
        # Display query history
        if self.history:
            with st.expander("Query History"):
                for i, item in enumerate(reversed(self.history)):
                    st.markdown(f"**Q{len(self.history)-i}:** {item['query']}")
                    st.markdown(f"**A{len(self.history)-i}:** {item['response'][:100]}...")
                    st.markdown("---")
