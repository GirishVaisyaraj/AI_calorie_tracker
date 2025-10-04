import streamlit as st
import plotly.express as px
from gemini_nutrition import estimate_nutrition
import io
from PIL import Image
import os
import pandas as pd
from database import init_db, add_meal, get_history

init_db()

st.title("AI Nutrition Tracker")

tab1, tab2 = st.tabs(["Current Meal", "Historical View"])

with tab1:
    # Input options
    input_type = st.radio("Input Type:", ["Image", "Text"])

    image = None
    text_description = None

    if input_type == "Image":
        uploaded_file = st.file_uploader("Upload an image of your meal:", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image.", use_column_width=True)
            with open("temp_image.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.image_path = "temp_image.jpg"
    elif input_type == "Text":
        text_description = st.text_area("Enter a description of your meal:")

    # Analyze button
    if st.button("Analyze"):
        if image is None and text_description is None:
            st.error("Please upload an image or enter a text description.")
        else:
            with st.spinner("Analyzing..."):
                # Get nutrition information
                image_path = st.session_state.get("image_path")
                nutrition_info = estimate_nutrition(image_path=image_path, text_description=text_description)

            if "error" in nutrition_info:
                st.error(f"Error: {nutrition_info['error']}")
            else:
                meal_summary = nutrition_info['meal_summary']
                dishes = nutrition_info['dishes']
                add_meal(meal_summary, dishes)

                # Donut chart for macronutrients
                macros = {
                    "Protein": meal_summary['total_protein_g'],
                    "Fat": meal_summary['total_fat_g'],
                    "Carbs": meal_summary['total_carbs_g']
                }
                colors = {'Protein': 'green', 'Fat': 'red', 'Carbs': 'orange'}
                fig = px.pie(values=list(macros.values()), names=list(macros.keys()), title="Macronutrient Distribution", hole=0.3, color=list(macros.keys()), color_discrete_map=colors)
                st.plotly_chart(fig)

                # Detailed macronutrient bars
                st.subheader("Macronutrient Details")
                total_macros = meal_summary['total_protein_g'] + meal_summary['total_fat_g'] + meal_summary['total_carbs_g']
                st.progress(int((meal_summary['total_protein_g'] / total_macros) * 100), text=f"Protein: {meal_summary['total_protein_g']}g")
                st.progress(int((meal_summary['total_fat_g'] / total_macros) * 100), text=f"Fat: {meal_summary['total_fat_g']}g")
                st.progress(int((meal_summary['total_carbs_g'] / total_macros) * 100), text=f"Carbs: {meal_summary['total_carbs_g']}g")

                # Calories per dish (horizontal bar chart)
                calories_per_dish = {dish['name']: dish['calories'] for dish in dishes}
                fig2 = px.bar(x=list(calories_per_dish.values()), y=list(calories_per_dish.keys()), orientation='h', labels={'x': 'Calories', 'y': 'Dish'})
                st.plotly_chart(fig2)

                # Stacked bar chart for macronutrient breakdown per dish
                dishes_df = pd.DataFrame(dishes)
                colors = {'protein_g': 'green', 'fat_g': 'red', 'carbs_g': 'orange'}
                fig8 = px.bar(dishes_df, x='name', y=['protein_g', 'fat_g', 'carbs_g'], title="Macronutrient Breakdown per Dish", color_discrete_map=colors)
                st.plotly_chart(fig8)

with tab2:
    st.header("Historical View")
    history_df = get_history()
    if not history_df.empty:
        view_type = st.radio("View Trend By:", ["Daily Summary", "Per Meal"])

        if view_type == "Daily Summary":
            # Convert 'date' to datetime and aggregate by day
            history_df['date'] = pd.to_datetime(history_df['date']).dt.date
            daily_summary = history_df.groupby('date').agg({
                'total_calories': 'sum',
                'total_protein_g': 'sum',
                'total_fat_g': 'sum',
                'total_carbs_g': 'sum'
            }).reset_index()
            
            # Convert date to string for categorical axis
            daily_summary['date'] = daily_summary['date'].astype(str)

            st.subheader("Daily Trends")
            plot_data = daily_summary
            x_axis = 'date'
            x_title = 'Date'
        
        else: # Per Meal
            st.subheader("Per Meal Trends")
            history_df['meal_number'] = range(1, len(history_df) + 1)
            plot_data = history_df
            x_axis = 'meal_number'
            x_title = 'Meal Number'


        # Calorie trend
        fig3 = px.line(plot_data, x=x_axis, y='total_calories', title="Calorie Trend", markers=True)
        fig3.update_xaxes(title_text=x_title)
        st.plotly_chart(fig3)

        # Stacked bar chart for macronutrient trends
        colors = {'total_protein_g': 'green', 'total_fat_g': 'red', 'total_carbs_g': 'orange'}
        fig4 = px.bar(plot_data, x=x_axis, y=['total_protein_g', 'total_fat_g', 'total_carbs_g'], title="Macronutrient Trends", color_discrete_map=colors)
        fig4.update_xaxes(title_text=x_title)
        st.plotly_chart(fig4)

        # Individual nutrient trend lines
        st.subheader("Individual Macronutrient Trends")
        fig5 = px.line(plot_data, x=x_axis, y='total_protein_g', title="Protein Trend", color_discrete_sequence=['green'], markers=True)
        fig5.update_xaxes(title_text=x_title)
        st.plotly_chart(fig5)
        fig6 = px.line(plot_data, x=x_axis, y='total_fat_g', title="Fat Trend", color_discrete_sequence=['red'], markers=True)
        fig6.update_xaxes(title_text=x_title)
        st.plotly_chart(fig6)
        fig7 = px.line(plot_data, x=x_axis, y='total_carbs_g', title="Carbs Trend", color_discrete_sequence=['orange'], markers=True)
        fig7.update_xaxes(title_text=x_title)
        st.plotly_chart(fig7)
    else:
        st.write("No historical data yet.")
