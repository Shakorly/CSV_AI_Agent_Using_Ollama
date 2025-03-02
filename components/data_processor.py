# components/data_processor.py
import pandas as pd
import numpy as np
import streamlit as st

class DataProcessor:
    """Component for processing and analyzing CSV data."""
    
    def clean_data(self, df):
        """Clean the DataFrame by handling missing values and outliers."""
        # Create a copy to avoid modifying the original
        cleaned_df = df.copy()
        
        # Display cleaning options
        st.sidebar.subheader("Cleaning Options")
        
        # Handle missing values
        missing_method = st.sidebar.selectbox(
            "Handle Missing Values",
            ["None", "Drop", "Fill with Mean", "Fill with Median", "Fill with Mode"]
        )
        
        if missing_method == "Drop":
            cleaned_df = cleaned_df.dropna()
        elif missing_method == "Fill with Mean":
            numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            cleaned_df[numeric_cols] = cleaned_df[numeric_cols].fillna(cleaned_df[numeric_cols].mean())
        elif missing_method == "Fill with Median":
            numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            cleaned_df[numeric_cols] = cleaned_df[numeric_cols].fillna(cleaned_df[numeric_cols].median())
        elif missing_method == "Fill with Mode":
            for col in cleaned_df.columns:
                cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mode()[0] if not cleaned_df[col].mode().empty else 0)
        
        # Handle duplicates
        if st.sidebar.checkbox("Remove Duplicates"):
            cleaned_df = cleaned_df.drop_duplicates()
        
        # Handle outliers for numeric columns
        if st.sidebar.checkbox("Handle Outliers"):
            numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                q1 = cleaned_df[col].quantile(0.25)
                q3 = cleaned_df[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                # Replace outliers with bounds
                cleaned_df[col] = cleaned_df[col].clip(lower_bound, upper_bound)
        
        return cleaned_df
    
    def generate_statistics(self, df):
        """Generate comprehensive statistics for the DataFrame."""
        stats = {}
        
        # Basic statistics
        stats["summary"] = df.describe().T
        
        # Missing value analysis
        stats["missing_values"] = pd.DataFrame({
            "Count": df.isna().sum(),
            "Percentage": (df.isna().sum() / len(df) * 100).round(2)
        })
        
        # Data types
        stats["data_types"] = pd.DataFrame({
            "Data Type": df.dtypes
        })
        
        # Unique values for categorical columns
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns
        stats["unique_values"] = {col: df[col].nunique() for col in categorical_cols}
        
        return stats