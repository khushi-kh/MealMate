import requests
import pandas as pd
import time
from main import app, db, MealsData

# BASE_URL = 'https://api.spoonacular.com/recipes/complexSearch'

# MEAL_TYPES = ['breakfast', 'lunch', 'snack', 'dinner']
# RECIPES_PER_MEAL_TYPE = 500
# PAGE_SIZE = 100  # Max allowed per Spoonacular API
# DELAY = 1  # Delay in seconds between requests

# def fetch_recipes(meal_type):
#     all_recipes = []
#     total_fetched = 0
#     offset = 0

#     while total_fetched < RECIPES_PER_MEAL_TYPE:
#         params = {
#             'apiKey': API_KEY,
#             'type': meal_type,
#             'addRecipeNutrition': True,
#             'number': PAGE_SIZE,
#             'offset': offset
#         }

#         response = requests.get(BASE_URL, params=params)
#         if response.status_code != 200:
#             print(f"❌ Error fetching {meal_type} at offset {offset}: {response.status_code}")
#             break

#         data = response.json()
#         results = data.get('results', [])
#         if not results:
#             print(f"⚠️ No more results for {meal_type}. Stopping.")
#             break

#         for item in results:
#             nutrients = {nut['name'].lower(): nut['amount'] for nut in item.get('nutrition', {}).get('nutrients', [])}
#             diets = item.get('diets', [])

#             recipe = {
#                 'name': item.get('title'),
#                 'meal_type': meal_type,
#                 'diet_type': ', '.join(diets) if diets else 'unknown',
#                 'calories': nutrients.get('calories', 0),
#                 'protein': nutrients.get('protein', 0),
#                 'fats': nutrients.get('fat', 0),
#                 'carbs': nutrients.get('carbohydrates', 0),
#                 'fiber': nutrients.get('fiber', 0),
#                 'sugar': nutrients.get('sugar', 0),
#                 'iron': nutrients.get('iron', 0),
#                 'sodium': nutrients.get('sodium', 0),
#                 'cholesterol': nutrients.get('cholesterol', 0),
#                 'recipe_link': f"https://spoonacular.com/recipes/{item['title'].replace(' ', '-')}-{item['id']}"
#             }

#             all_recipes.append(recipe)
#             total_fetched += 1

#             if total_fetched >= RECIPES_PER_MEAL_TYPE:
#                 break

#         offset += PAGE_SIZE
#         print(f"✅ {meal_type.capitalize()}: {total_fetched} recipes fetched so far...")
#         time.sleep(DELAY)

#     return all_recipes

# def extract_all():
#     full_data = []
#     for meal_type in MEAL_TYPES:
#         print(f"\n🚀 Starting extraction for: {meal_type}")
#         data = fetch_recipes(meal_type)
#         full_data.extend(data)

#     df = pd.DataFrame(full_data)
#     df.to_csv('meals_data.csv', index=False)
#     print(f"\n✅ Extraction complete! Total recipes: {len(df)}")
#     print("📄 Saved to meals_data.csv")


# def populate_meals_table(csv_path='D:/Khushi/Python Practice/Python Projects/MealMate/data/cleaned_data.csv'):
#     df = pd.read_csv(csv_path)

#     for _, row in df.iterrows():
#         meal = MealsData(
#             name=row['name'],
#             meal_type=row['meal_type'],
#             diet_type = row['diet_type'],
#             vegetarian = row['vegetarian'],
#             vegan = row['vegan'],
#             non_vegetarian = row['non_vegetarian'],
#             ketogenic = row['ketogenic'],
#             dairy_free = row['dairy_free'],
#             gluten_free = row['gluten_free'],
#             calories=row.get('calories'),
#             protein=row.get('protein'),
#             fats=row.get('fats'),
#             carbs=row.get('carbs'),
#             fiber=row.get('fiber'),
#             sugar=row.get('sugar'),
#             iron=row.get('iron'),
#             sodium=row.get('sodium'),
#             cholesterol=row.get('cholesterol'),
#             recipe_link=row.get('recipe_link'))
#         db.session.add(meal)

#     db.session.commit()
#     print("Executed Successfully")


# if __name__ == '__main__':
#    # extract_all()
#    with app.app_context():
#         populate_meals_table()


