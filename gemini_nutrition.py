from google import genai
import os
from pydantic import BaseModel
from typing import List, Optional
# Define the schema for structured response
class DishNutrition(BaseModel):
    name: str
    estimated_weight: float
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
    total_fiber_g: float

class MealNutrition(BaseModel):
    total_calories: float
    total_protein_g: float
    total_fat_g: float
    total_carbs_g: float
    total_fiber_g:  float
    #dishes: list[DishNutrition]

class MealAnalysis(BaseModel):
    dishes: List[DishNutrition]
    meal_summary: MealNutrition
api_key = os.getenv("MY_VAR")
client = genai.Client(api_key=api_key)
# Set up Gemini client
client = genai.Client(api_key=api_key)

# Estimate nutrition using Gemini API
def estimate_nutrition(image_path=None, text_description=None):
    #print(image,image)
    try:
        if image_path:
            uploaded_image = client.files.upload(file=image_path) # Keep this line if you want to allow image upload
        else:
            uploaded_image = None

        contents = []
        if uploaded_image:
            contents.append(uploaded_image)
        if text_description:
            contents.append(text_description)


        # Define the prompt
        prompt = (
            "Analyze the provided information (image and/or text description) and "
            "provide nutritional information for each dish, as well as a summary for the entire meal."
        )

        # Generate content with the specified response schema
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,  # Use the combined contents list
            config={
                "response_mime_type": "application/json",
                "response_schema": MealAnalysis,
            },
        )

        # Access the structured response
        meal_analysis= response.parsed
        return meal_analysis.model_dump()

    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    analysed_response=estimate_nutrition(image_path='temp_image.jpg',text_description=' chicken breast is of 200g')

    dishes=analysed_response['dishes']
    meal_summary=analysed_response['meal_summary']


    print('**** dishes****')
    for dish in dishes:
        for key,value in dish.items():
            print(f'{key}: {value}\n')

    print('**** meal summary value****')
    for key,value in meal_summary.items():
            print(f'{key}: {value}\n')
