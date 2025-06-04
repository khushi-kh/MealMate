from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, ForeignKey, Date, Float, func, or_, and_
from forms import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, LoginManager, UserMixin, logout_user, login_required
from datetime import datetime, date, timedelta
import random
from dashboard import PieChart, LineChart, Table, KPI
import pandas as pd
import os
from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()
load_dotenv = load_dotenv(dotenv_path)

year = datetime.now().year
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'fallback-key'
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app=app)

# # Creating DB
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI', 'sqlite:///D:/Khushi/Python Practice/Python Projects/MealMate/instance/mealmate_db.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app=app)

# Creating MealsData Table
class MealsData(db.Model):
    __tablename__ = 'meals_data'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    meal_type: Mapped[str] = mapped_column(String(250))
    diet_type: Mapped[str] = mapped_column(String(250))
    vegetarian: Mapped[int] =  mapped_column(Integer)
    vegan: Mapped[int] =  mapped_column(Integer)
    non_vegetarian: Mapped[int] =  mapped_column(Integer)
    ketogenic: Mapped[int] =  mapped_column(Integer)
    dairy_free: Mapped[int] =  mapped_column(Integer)
    gluten_free: Mapped[int] =  mapped_column(Integer)
    calories: Mapped[float] = mapped_column(Float)
    protein: Mapped[float] = mapped_column(Float)
    fats: Mapped[float] = mapped_column(Float)
    carbs: Mapped[float] = mapped_column(Float)
    fiber: Mapped[float] = mapped_column(Float)
    sugar: Mapped[float] = mapped_column(Float)
    iron: Mapped[float] = mapped_column(Float)
    sodium: Mapped[float] = mapped_column(Float)
    cholesterol: Mapped[float] = mapped_column(Float)
    recipe_link: Mapped[str] = mapped_column(String, nullable=True)

# Creating Users Table
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(250), nullable=False)


# Creating MealLog Table
class MealLog(db.Model):
    __tablename__= 'meal_log'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id : Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    date: Mapped[date] = mapped_column(Date, default=func.current_date(), nullable=False) # type: ignore
    diet_type : Mapped[str] = mapped_column(String(250))

    breakfast_id: Mapped[int] = mapped_column(Integer, ForeignKey('meals_data.id'), nullable=True)
    lunch_id: Mapped[int] = mapped_column(Integer, ForeignKey('meals_data.id'), nullable=True)
    snack_id: Mapped[int] = mapped_column(Integer, ForeignKey('meals_data.id'), nullable=True)
    dinner_id: Mapped[int] = mapped_column(Integer, ForeignKey('meals_data.id'), nullable=True)

    user = relationship('User', backref='meal_logs')
    breakfast = relationship('MealsData', foreign_keys=[breakfast_id])
    lunch = relationship('MealsData', foreign_keys=[lunch_id])
    snack = relationship('MealsData', foreign_keys=[snack_id])
    dinner = relationship('MealsData', foreign_keys=[dinner_id])


# Creating NutrientLog Table
class NutrientLog(db.Model):
    __tablename__ = 'nutrients_log'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    date: Mapped[date] = mapped_column(Date, default=func.current_date(), nullable=False) # type: ignore
    calories: Mapped[float] = mapped_column(Float)
    protein: Mapped[float] = mapped_column(Float)
    fats: Mapped[float] = mapped_column(Float)
    carbs: Mapped[float] = mapped_column(Float)
    fiber: Mapped[float] = mapped_column(Float)
    sugar: Mapped[float] = mapped_column(Float)
    iron: Mapped[float] = mapped_column(Float)
    sodium: Mapped[float] = mapped_column(Float)
    cholesterol: Mapped[float] = mapped_column(Float)

    user = relationship('User', backref='nutrient_logs')


#Create Table Schema
with app.app_context():
    db.create_all()

# Function to calculate total nutrients
def calculate_total_nutrients(meal_data):
    nutrients = {
        'calories': 0,
        'protein': 0,
        'fats': 0,
        'carbs': 0,
        'fiber': 0,
        'sugar': 0,
        'iron': 0,
        'sodium': 0,
        'cholesterol': 0
    }

    for meal_id in meal_data.values():
        if meal_id is None:
            continue
        meal = MealsData.query.get(meal_id)
        if not meal:
            continue
        for nutrient in nutrients:
            nutrients[nutrient] += getattr(meal, nutrient, 0)

    return nutrients


@app.route('/')
def home():
    return render_template('index.html', year=year)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # check if user email is already present in db
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()

        if user:
            flash("Psst. Email is already registered. LogIn instead", category='error')
            return redirect(url_for('register'))
        
        hash_password = generate_password_hash(
            form.password.data,
            method= 'pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            email = form.email.data,
            name = form.name.data,
            password = hash_password,)
        
        db.session.add(new_user)
        print(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('welcome_user'))
        
    return render_template('register.html', form=form, current_user=current_user, year=year)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Returns None if user not found

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email==form.email.data))
        user = result.scalar()

        # if email doesn't exist
        if not user:
            flash('That Email is not registered. Please Try Again')
            return redirect(url_for('login'))
        
        # password mismatch
        elif not check_password_hash(user.password, password):
            flash("Incorrect Password. Please Try Again")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('welcome_user'))
        
    return render_template('login.html', form=form, current_user=current_user, year=year)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/welcome')
@login_required
def welcome_user():
    return render_template('welcome.html', year=year)


@app.route('/select_preference')
@login_required
def recommendation():
    return render_template('recommendation.html', year=year)


@app.route('/suggestions', methods=['POST'])
@login_required
def show_suggestions():
    selected_diets = request.form.get('diet_types', '').split(',')
    print(selected_diets)
    selected_meals = request.form.get('meal_types', '').split(',')
    print(selected_meals)

    # Get meals selected by user in the last 7 days
    seven_days_ago = date.today() - timedelta(days=7)
    recent_meal_logs = MealLog.query.filter(
        MealLog.user_id == current_user.id,
        MealLog.date >= seven_days_ago
    ).all()
    print(recent_meal_logs)
    # Collect all meal IDs from the last 7 days
    excluded_meal_ids = set()
    for log in recent_meal_logs:
        if log.breakfast_id:
            excluded_meal_ids.add(log.breakfast_id)
        if log.lunch_id:
            excluded_meal_ids.add(log.lunch_id)
        if log.snack_id:
            excluded_meal_ids.add(log.snack_id)
        if log.dinner_id:
            excluded_meal_ids.add(log.dinner_id)
    
    print(f"Excluded meal IDs from last 7 days: {excluded_meal_ids}")

    all_recommendations = {}
    fallback_msg = {}

    for meal_type in selected_meals:
        # Base query excluding recent meals
        base_query = MealsData.query.filter(MealsData.meal_type == meal_type)
        if excluded_meal_ids:
            base_query = base_query.filter(~MealsData.id.in_(excluded_meal_ids))

        
        # First try: meals that match ALL selected diets (excluding recent meals)
        all_matching_meals = base_query.filter(
            *[MealsData.diet_type.ilike(f'%{diet}%') for diet in selected_diets]
        ).all()
        
        # Randomly select up to 5 meals from the matching results
        if len(all_matching_meals) >= 5:
            meals = random.sample(all_matching_meals, 5)
        else:
            meals = all_matching_meals
        
        print(f"First try for {meal_type}: {len(meals)} meals selected from {len(all_matching_meals)} available")

        if len(meals) < 5:
            # Second try: meals that match ANY selected diet (excluding recent meals)
            all_matching_meals = base_query.filter(
                or_(*[MealsData.diet_type.ilike(f'%{diet}%') for diet in selected_diets])
            ).all()
            
            # Remove already selected meals to avoid duplicates
            available_meals = [meal for meal in all_matching_meals if meal not in meals]
            
            if len(available_meals) >= (5 - len(meals)):
                additional_meals = random.sample(available_meals, 5 - len(meals))
                meals.extend(additional_meals)
            else:
                meals.extend(available_meals)
            
            print(f"Second try for {meal_type}: {len(meals)} total meals selected")

            if len(meals) < 5:
                # Third try: any meals of this type (excluding recent meals)
                all_available_meals = base_query.all()
                
                # Remove already selected meals to avoid duplicates
                available_meals = [meal for meal in all_available_meals if meal not in meals]
                
                if len(available_meals) >= (5 - len(meals)):
                    additional_meals = random.sample(available_meals, 5 - len(meals))
                    meals.extend(additional_meals)
                else:
                    meals.extend(available_meals)
                
                print(f"Third try for {meal_type}: {len(meals)} total meals selected")
                
                if len(meals) < 5:
                    # Final fallback: include recent meals if necessary
                    fallback_msg[meal_type] = (
                        f"Limited {meal_type} options available. "
                        f"Some recently selected meals may be included."
                    )
                    all_meals = MealsData.query.filter(
                        MealsData.meal_type == meal_type
                    ).all()
                    
                    # Remove already selected meals to avoid duplicates
                    available_meals = [meal for meal in all_meals if meal not in meals]
                    
                    if len(available_meals) >= (5 - len(meals)):
                        additional_meals = random.sample(available_meals, 5 - len(meals))
                        meals.extend(additional_meals)
                    else:
                        meals.extend(available_meals)
                    
                    print(f"Final fallback for {meal_type}: {len(meals)} total meals selected")
                elif not any(diet.lower() in (meal.diet_type or '').lower() for diet in selected_diets for meal in meals):
                    fallback_msg[meal_type] = (
                        f"{', '.join([d.capitalize() for d in selected_diets])} "
                        f"{meal_type.capitalize()} suggestions could not be found in our database. "
                        f"Here are some other {meal_type} options instead."
                    )

        # Shuffle the final list to ensure randomness in display order
        random.shuffle(meals)
        all_recommendations[meal_type] = meals
        print(f"Final recommendations for {meal_type}: {[meal.name for meal in meals]}")

    return render_template('suggestions.html', suggestions=all_recommendations, year=year, fallback_msg=fallback_msg)


@app.route('/selected_meals', methods=['POST'])
@login_required
def results():
    selections = {key: value for key, value in request.form.items()}
    print("Selections:", selections)

    information = {}
    meal_log = {}
    for meal_type, meal_id in selections.items():
        try:
            meal_id = int(meal_id)  # Safely cast to int
            meal = MealsData.query.filter_by(id=meal_id).first()
            if meal:
                information[meal_type] = meal
                meal_log[f"{meal_type}_id"] = meal_id
            else:
                print(f"No meal found with ID: {meal_id}")
        except ValueError:
            print(f"Invalid meal ID received: {meal_id}")
            continue
    print(information)
    session['selected_meals'] = meal_log
    print(session)

    return render_template('results.html', year=year, information=information)


@app.route('/save_logs', methods=['GET'])
@login_required
def save_logs():
    meal_data = session.get('selected_meals')
    if not meal_data:
        flash("No meal selections found. Please try again.", category="error")
        return redirect(url_for('selected_meals'))

    today = date.today()
    diet_type = request.args.get('diet_type', 'custom')

    # --------- Handle MealLog (update or create) ----------
    existing_log = MealLog.query.filter_by(user_id=current_user.id, date=today).first()
    if existing_log:
        if meal_data.get('breakfast_id') is not None:
            existing_log.breakfast_id = meal_data['breakfast_id']
        if meal_data.get('lunch_id') is not None:
            existing_log.lunch_id = meal_data['lunch_id']
        if meal_data.get('snack_id') is not None:
            existing_log.snack_id = meal_data['snack_id']
        if meal_data.get('dinner_id') is not None:
            existing_log.dinner_id = meal_data['dinner_id']
        if diet_type:
            existing_log.diet_type = diet_type
    else:
        new_log = MealLog(
            user_id=current_user.id,
            date=today,
            diet_type=diet_type,
            breakfast_id=meal_data.get('breakfast_id'),
            lunch_id=meal_data.get('lunch_id'),
            snack_id=meal_data.get('snack_id'),
            dinner_id=meal_data.get('dinner_id')
        )
        db.session.add(new_log)

    # --------- Handle NutrientLog (update or create) ----------
    total_nutrients = calculate_total_nutrients(meal_data)

    existing_nutrient_log = NutrientLog.query.filter_by(user_id=current_user.id, date=today).first()
    if existing_nutrient_log:
        for nutrient, value in total_nutrients.items():
            setattr(existing_nutrient_log, nutrient, value)
    else:
        new_nutrient_log = NutrientLog(
            user_id=current_user.id,
            date=today,
            **total_nutrients
        )
        db.session.add(new_nutrient_log)

    # --------- Commit once ----------
    db.session.commit()

    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Filter past 7 days of logs
    today = date.today()
    last_week = today - timedelta(days=7)
    
    logs = NutrientLog.query.filter(
        NutrientLog.user_id == current_user.id,
        NutrientLog.date >= last_week
    ).order_by(NutrientLog.date).all()

    today_meal_log = MealLog.query.filter(
        MealLog.user_id == current_user.id,
        MealLog.date == today
    ).first()

    todays_meals = {}
    if today_meal_log:
        meal_mappings = {
            'breakfast': today_meal_log.breakfast_id,
            'lunch': today_meal_log.lunch_id,
            'snack': today_meal_log.snack_id,
            'dinner': today_meal_log.dinner_id
        }
        
        for meal_type, meal_id in meal_mappings.items():
            if meal_id:  # Only fetch if meal_id exists
                meal = MealsData.query.get(meal_id)
                if meal:
                    todays_meals[meal_type] = meal
    
    
    if not logs:
        flash("No data found for dashboard. Log some meals first.", "info")
        return render_template('dashboard.html', year=year)
    
    # Convert to DataFrame
    data = [{
        'date': log.date,
        'calories': log.calories,
        'protein': log.protein,
        'fats': log.fats,
        'carbs': log.carbs,
        'fiber': log.fiber,
        'sugar': log.sugar,
        'iron': log.iron,
        'sodium': log.sodium,
        'cholesterol': log.cholesterol
    } for log in logs]
    
    df = pd.DataFrame(data)
    today_df = df[df['date'] == today]

    pie_chart = PieChart.nutrient_breakdown(df)
    line_chart = LineChart.calories_over_time(df)
    kpi = KPI.kpi(today_df)

    # Cleanup session
    session.pop('selected_meals', None)

    return render_template(
        'dashboard.html',
        year=year,
        pie_chart=pie_chart,
        line_chart=line_chart,
        information=todays_meals,
        kpi=kpi,
        current_user=current_user
    )


if __name__ == '__main__':
    app.run(debug=True)
