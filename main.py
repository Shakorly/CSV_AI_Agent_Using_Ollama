# main.py - Entry point for the application
import streamlit as st
from components.file_handler import FileHandler
from components.data_processor import DataProcessor
from components.ai_engine import OllamaEngine
from components.visualizer import Visualizer
from components.query_interface import QueryInterface

def main():
    st.set_page_config(page_title="CSV Analysis Agent", layout="wide")
    
    st.title("CSV Analysis Agent")
    st.sidebar.header("Configuration")
    
    # Initialize components
    file_handler = FileHandler()
    data_processor = DataProcessor()
    ai_engine = OllamaEngine()
    visualizer = Visualizer()
    query_interface = QueryInterface(ai_engine)
    
    # File upload section
    uploaded_file = file_handler.upload_file()
    
    if uploaded_file:
        # Load and process data
        df = file_handler.load_csv(uploaded_file)
        if df is not None:
            # Display data overview
            st.subheader("Data Overview")
            st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
            st.dataframe(df.head())
            
            # Data processing options
            st.sidebar.subheader("Data Processing")
            if st.sidebar.checkbox("Clean Data"):
                df = data_processor.clean_data(df)
                st.success("Data cleaned successfully")
            
            if st.sidebar.checkbox("Generate Summary Statistics"):
                stats = data_processor.generate_statistics(df)
                st.subheader("Summary Statistics")
                st.write(stats)
            
            # Visualizations
            st.sidebar.subheader("Visualizations")
            viz_type = st.sidebar.selectbox(
                "Select Visualization Type",
                ["None", "Correlation Matrix", "Histogram", "Scatter Plot", "Bar Chart", "Box Plot"]
            )
            
            if viz_type != "None":
                st.subheader(f"{viz_type} Visualization")
                visualizer.create_visualization(df, viz_type)
            
            # AI Query Interface
            st.subheader("Ask Questions About Your Data")
            query_interface.process_query(df)
    
    # Add footer
    st.markdown("---")
    st.markdown("CSV Analysis Agent | Built with Streamlit and Ollama")

if __name__ == "__main__":
    main()
