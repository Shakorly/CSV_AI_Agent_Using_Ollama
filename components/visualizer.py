# components/visualizer.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

class Visualizer:
    """Component for creating visualizations from DataFrame."""
    
    def create_visualization(self, df, viz_type):
        """Create and display visualizations based on the selected type."""
        try:
            if viz_type == "Correlation Matrix":
                self._plot_correlation_matrix(df)
            elif viz_type == "Histogram":
                self._plot_histogram(df)
            elif viz_type == "Scatter Plot":
                self._plot_scatter(df)
            elif viz_type == "Bar Chart":
                self._plot_bar_chart(df)
            elif viz_type == "Box Plot":
                self._plot_box_plot(df)
        except Exception as e:
            st.error(f"Error creating visualization: {str(e)}")
    
    def _plot_correlation_matrix(self, df):
        """Create and display a correlation matrix."""
        # Get numeric columns
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            st.warning("No numeric columns found for correlation matrix.")
            return
        
        # Calculate correlation
        corr = numeric_df.corr()
        
        # Create heatmap using Plotly
        fig = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu_r"
        )
        fig.update_layout(
            title="Correlation Matrix",
            height=600,
            width=800
        )
        
        st.plotly_chart(fig)
    
    def _plot_histogram(self, df):
        """Create and display a histogram for selected column."""
        # Select column for histogram
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_columns:
            st.warning("No numeric columns found for histogram.")
            return
        
        selected_column = st.selectbox("Select Column for Histogram", numeric_columns)
        
        # Create histogram
        fig = px.histogram(
            df,
            x=selected_column,
            nbins=st.slider("Number of Bins", 5, 100, 20),
            marginal="box",  # Add a box plot at the margin
            title=f"Histogram of {selected_column}"
        )
        
        st.plotly_chart(fig)
    
    def _plot_scatter(self, df):
        """Create and display a scatter plot for selected columns."""
        # Select columns for scatter plot
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_columns) < 2:
            st.warning("Need at least two numeric columns for scatter plot.")
            return
        
        x_column = st.selectbox("Select X-axis Column", numeric_columns, index=0)
        y_column = st.selectbox("Select Y-axis Column", numeric_columns, index=min(1, len(numeric_columns)-1))
        
        # Optional color column
        color_options = ["None"] + df.columns.tolist()
        color_column = st.selectbox("Color by", color_options)
        color = None if color_column == "None" else color_column
        
        # Create scatter plot
        fig = px.scatter(
            df,
            x=x_column,
            y=y_column,
            color=color,
            title=f"Scatter Plot: {x_column} vs {y_column}",
            opacity=0.7,
            size_max=10,
            render_mode="webgl"  # For better performance with large datasets
        )
        
        # Add regression line if requested
        if st.checkbox("Add Regression Line"):
            fig.update_layout(
                shapes=[{
                    'type': 'line',
                    'x0': df[x_column].min(),
                    'y0': np.polyval(np.polyfit(df[x_column], df[y_column], 1), df[x_column].min()),
                    'x1': df[x_column].max(),
                    'y1': np.polyval(np.polyfit(df[x_column], df[y_column], 1), df[x_column].max()),
                    'line': {
                        'color': 'red',
                        'width': 2,
                        'dash': 'dash',
                    },
                }]
            )
        
        st.plotly_chart(fig)
    
    def _plot_bar_chart(self, df):
        """Create and display a bar chart for selected columns."""
        # Get columns that might be good for bar charts (categorical or low cardinality)
        all_columns = df.columns.tolist()
        categorical_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()
        
        # Add numeric columns with low cardinality
        for col in df.select_dtypes(include=[np.number]).columns:
            if df[col].nunique() <= 20:  # Arbitrary threshold for "low cardinality"
                categorical_columns.append(col)
        
        if not categorical_columns:
            st.warning("No suitable columns found for bar chart.")
            return
        
        # Select columns for bar chart
        x_column = st.selectbox("Select Category Column (X-axis)", categorical_columns)
        
        # For Y-axis, use either count or a numeric column
        y_options = ["Count"] + df.select_dtypes(include=[np.number]).columns.tolist()
        y_column = st.selectbox("Select Value Column (Y-axis)", y_options)
        
        # Create the figure
        if y_column == "Count":
            # Count plot
            value_counts = df[x_column].value_counts().reset_index()
            value_counts.columns = [x_column, 'count']
            fig = px.bar(
                value_counts,
                x=x_column,
                y='count',
                title=f"Count of {x_column}"
            )
        else:
            # Aggregation
            agg_func = st.selectbox(
                "Aggregation Function",
                ["Mean", "Sum", "Median", "Min", "Max", "Count"]
            )
            
            # Map selection to pandas aggregation function
            agg_map = {
                "Mean": "mean",
                "Sum": "sum",
                "Median": "median",
                "Min": "min",
                "Max": "max",
                "Count": "count"
            }
            
            # Create grouped data
            grouped_data = df.groupby(x_column)[y_column].agg(agg_map[agg_func]).reset_index()
            
            # Create bar chart
            fig = px.bar(
                grouped_data,
                x=x_column,
                y=y_column,
                title=f"{agg_func} of {y_column} by {x_column}"
            )
        
        # Customize the chart
        fig.update_layout(xaxis_tickangle=-45)
        
        st.plotly_chart(fig)
    
    def _plot_box_plot(self, df):
        """Create and display a box plot for selected columns."""
        # Get numeric columns for box plot
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_columns:
            st.warning("No numeric columns found for box plot.")
            return
        
        # Select columns
        y_column = st.selectbox("Select Value Column (Y-axis)", numeric_columns)
        
        # Optional grouping column
        group_options = ["None"] + df.columns.tolist()
        x_column = st.selectbox("Group by (X-axis)", group_options)
        
        # Create box plot
        if x_column == "None":
            fig = px.box(
                df,
                y=y_column,
                title=f"Box Plot of {y_column}"
            )
        else:
            fig = px.box(
                df,
                x=x_column,
                y=y_column,
                title=f"Box Plot of {y_column} grouped by {x_column}"
            )
        
        # Add individual points if requested
        if st.checkbox("Show Individual Points"):
            fig.update_traces(boxpoints="all", jitter=0.3)
        
        st.plotly_chart(fig) 
