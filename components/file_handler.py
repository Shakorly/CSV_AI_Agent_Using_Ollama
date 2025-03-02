# components/file_handler.py
import streamlit as st
import pandas as pd
import io

class FileHandler:
    """Component for handling file uploads and loading CSV data."""
    
    def upload_file(self):
        """Create a file uploader widget and return the uploaded file."""
        uploaded_file = st.sidebar.file_uploader(
            "Upload CSV File",
            type=["csv"],
            help="Upload a CSV file to analyze"
        )
        return uploaded_file
    
    def load_csv(self, uploaded_file):
        """Load a CSV file into a pandas DataFrame."""
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            return df
        except Exception as e:
            st.error(f"Error loading CSV file: {str(e)}")
            return None
    
    def export_processed_data(self, df):
        """Export the processed DataFrame as a CSV file."""
        if df is not None:
            csv = df.to_csv(index=False)
            b64 = io.StringIO()
            b64.write(csv)
            
            download_button = st.download_button(
                label="Download Processed Data",
                data=b64.getvalue(),
                file_name="processed_data.csv",
                mime="text/csv"
            )
            return download_button
        return None
