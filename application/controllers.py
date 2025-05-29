from flask import current_app as app, jsonify, request, render_template, send_file
from flask_security import auth_required, roles_required
from werkzeug.security import generate_password_hash, check_password_hash
from .sec import datastore
from application.models import User, SymptomOutcome, FoodIntake, Meal
from flask_restful import fields, marshal
from datetime import datetime, timedelta
from application.database import db
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import and_
import pandas as pd
import numpy as np
import io
import os
import sklearn
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from application.vector_db import create_vector_db
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_models import ChatCohere
from IPython.display import Markdown
from application.validation import ValidationError
from datetime import datetime
from main import user_vector_dbs

# Create a new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(
        name=data['name'],
        email=data['email'],
        password=data['password'],
    )
    if "@" not in user.email:
        raise ValidationError(status_code=400, error_code="UVE1006", error_message="Not a valid email")
    if len(user.password)<7:
        raise ValidationError(status_code=400, error_code="UVE1007", error_message="Password should have atleast 8 letters")
    if user.name is None:
        raise ValidationError(status_code=400, error_code="UVE1002", error_message="username is required")
    if user.password is None:
        raise ValidationError(status_code=400, error_code="UVE1003", error_message="password is required")
    
    now_user_name=User.query.filter_by(name=user.name).first()
    if now_user_name:
        raise ValidationError(status_code=400, error_code="UVE1004", error_message="duplicate username")
    
    if not datastore.find_user(email=user.email):
        new_user=datastore.create_user(name=user.name, email=user.email, password=generate_password_hash(user.password, method="pbkdf2:sha256"), roles=['user'])
        db.session.commit()
    return jsonify({"message": "User created", "user_id": user.id}), 201

# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "active": user.active,
        "fs_uniquifier": user.fs_uniquifier
    } for user in users]
    return jsonify(users_list)

# Get a user by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "active": user.active,
        "fs_uniquifier": user.fs_uniquifier
    })

# Delete a user by ID
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})

# Create a new symptom outcome
@app.route('/symptoms/<int:user_id>', methods=['POST'])
def create_symptom(user_id):
    data = request.get_json()
    today = datetime.today().date()
    exists = SymptomOutcome.query.filter_by(user_id=user_id).filter(db.func.date(SymptomOutcome.date) == today).first()
    if exists:
        return jsonify({"error": "Symptom already submitted for today"}), 400

    # Convert string "1"/"0" to int
    bool_fields = [
        'pain_while_passing_stool', 'mucous_in_stool', 'blood_in_stool',
        'fever', 'nausea', 'flatulence'
    ]
    for field in bool_fields:
        if field in data:
            # Accept both string and int
            data[field] = int(data[field])

    symptom = SymptomOutcome(
        user_id=user_id,
        date=datetime.today(),
        stool_consistency=data['stool_consistency'],
        pain_while_passing_stool=data['pain_while_passing_stool'],
        stool_colour=data['stool_colour'],
        stool_frequency=data['stool_frequency'],
        mucous_in_stool=data['mucous_in_stool'],
        blood_in_stool=data['blood_in_stool'],
        pain_location=data['pain_location'],
        fever=data['fever'],
        nausea=data['nausea'],
        flatulence=data['flatulence']
    )
    db.session.add(symptom)
    db.session.commit()
    return jsonify({"message": "SymptomOutcome created", "id": symptom.id}), 201

# Get all symptoms for a user
@app.route('/symptoms/user/<int:user_id>', methods=['GET'])
def get_symptoms_for_user(user_id):
    symptoms = SymptomOutcome.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": s.id,
        "date": s.date.isoformat(),
        "stool_consistency": s.stool_consistency,
        "pain_while_passing_stool": s.pain_while_passing_stool,
        "stool_colour": s.stool_colour,
        "stool_frequency": s.stool_frequency,
        "mucous_in_stool": s.mucous_in_stool,
        "blood_in_stool": s.blood_in_stool,
        "pain_location": s.pain_location,
        "fever": s.fever,
        "nausea": s.nausea,
        "flatulence": s.flatulence
    } for s in symptoms])

# Get a symptom by ID
@app.route('/symptoms/<int:symptom_id>', methods=['GET'])
def get_symptom(symptom_id):
    s = SymptomOutcome.query.get_or_404(symptom_id)
    return jsonify({
        "id": s.id,
        "user_id": s.user_id,
        "date": s.date.isoformat(),
        "stool_consistency": s.stool_consistency,
        "pain_while_passing_stool": s.pain_while_passing_stool,
        "stool_colour": s.stool_colour,
        "stool_frequency": s.stool_frequency,
        "mucous_in_stool": s.mucous_in_stool,
        "blood_in_stool": s.blood_in_stool,
        "pain_location": s.pain_location,
        "fever": s.fever,
        "nausea": s.nausea,
        "flatulence": s.flatulence
    })

# Update a symptom by ID
@app.route('/symptoms/<int:symptom_id>', methods=['PUT'])
def update_symptom(symptom_id):
    s = SymptomOutcome.query.get_or_404(symptom_id)
    data = request.get_json()
    # Convert string "1"/"0" to int for boolean fields
    bool_fields = [
        'pain_while_passing_stool', 'mucous_in_stool', 'blood_in_stool',
        'fever', 'nausea', 'flatulence'
    ]
    for field in bool_fields:
        if field in data:
            data[field] = int(data[field])
    for field in ['stool_consistency', 'pain_while_passing_stool', 'stool_colour',
                  'stool_frequency', 'mucous_in_stool', 'blood_in_stool', 'pain_location',
                  'fever', 'nausea', 'flatulence']:
        if field in data:
            setattr(s, field, data[field])
    db.session.commit()
    return jsonify({"message": "SymptomOutcome updated"})

# Delete a symptom by ID
@app.route('/symptoms/<int:symptom_id>', methods=['DELETE'])
def delete_symptom(symptom_id):
    s = SymptomOutcome.query.get_or_404(symptom_id)
    db.session.delete(s)
    db.session.commit()
    return jsonify({"message": "SymptomOutcome deleted"})

# Create a new food intake
@app.route('/food/<int:user_id>', methods=['POST'])
def create_food(user_id):
    data = request.get_json()
    today = datetime.today().date()
    exists = FoodIntake.query.filter_by(user_id=user_id).filter(db.func.date(FoodIntake.date) == today).first()
    if exists:
        return jsonify({"error": "Food already submitted for today"}), 400
    food = FoodIntake(
        user_id=user_id,
        date=datetime.today(),
        water=data['water'],
        stress=data['stress']
    )
    db.session.add(food)
    db.session.commit()
    return jsonify({"message": "FoodIntake created", "id": food.id}), 201

# Get all food intakes for a user
@app.route('/food/user/<int:user_id>', methods=['GET'])
def get_food_for_user(user_id):
    foods = FoodIntake.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": f.id,
        "date": f.date.isoformat(),
        "water": f.water,
        "stress": f.stress
    } for f in foods])

# Get a food intake by ID
@app.route('/food/<int:food_id>', methods=['GET'])
def get_food(food_id):
    f = FoodIntake.query.get_or_404(food_id)
    return jsonify({
        "id": f.id,
        "user_id": f.user_id,
        "date": f.date.isoformat(),
        "water": f.water,
        "stress": f.stress
    })

# Update a food intake by ID
@app.route('/food/<int:food_id>', methods=['PUT'])
def update_food(food_id):
    f = FoodIntake.query.get_or_404(food_id)
    data = request.get_json()
    for field in ['water', 'stress']:
        if field in data:
            setattr(f, field, data[field])
    db.session.commit()
    return jsonify({"message": "FoodIntake updated"})

# Delete a food intake by ID
@app.route('/food/<int:food_id>', methods=['DELETE'])
def delete_food(food_id):
    f = FoodIntake.query.get_or_404(food_id)
    db.session.delete(f)
    db.session.commit()
    return jsonify({"message": "FoodIntake deleted"})
# Create a new meal
@app.route('/meals/<int:user_id>', methods=['POST'])
def create_meal(user_id):
    data = request.get_json()
    user_id = user_id
    today = datetime.today().date()
    # Try to find today's FoodIntake for this user
    food_intake = FoodIntake.query.filter_by(user_id=user_id).filter(db.func.date(FoodIntake.date) == today).first()
    if not food_intake:
        # Create a new FoodIntake with None for water and stress
        food_intake = FoodIntake(
            user_id=user_id,
            date=datetime.today(),
            water=None,
            stress=None
        )
        db.session.add(food_intake)
        db.session.commit()
    meal = Meal(
        food_intake_id=food_intake.id,
        meal_type=data['meal_type'],
        item=data['item']
    )
    db.session.add(meal)
    db.session.commit()
    return jsonify({"message": "Meal created", "id": meal.id}), 201

# Get all meals for a food intake
@app.route('/meals/food/<int:food_intake_id>', methods=['GET'])
def get_meals_for_food(food_intake_id):
    meals = Meal.query.filter_by(food_intake_id=food_intake_id).all()
    return jsonify([{
        "id": m.id,
        "food_intake_id": m.food_intake_id,
        "meal_type": m.meal_type,
        "item": m.item
    } for m in meals])

# Get a meal by ID
@app.route('/meals/<int:meal_id>', methods=['GET'])
def get_meal(meal_id):
    m = Meal.query.get_or_404(meal_id)
    return jsonify({
        "id": m.id,
        "food_intake_id": m.food_intake_id,
        "meal_type": m.meal_type,
        "item": m.item
    })

# Update a meal by ID
@app.route('/meals/<int:meal_id>', methods=['PUT'])
def update_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    data = request.get_json()
    if 'meal_type' in data:
        meal.meal_type = data['meal_type']
    if 'item' in data:
        meal.item = data['item']
    db.session.commit()
    return jsonify({"message": "Meal updated"})

# Delete a meal by ID
@app.route('/meals/<int:meal_id>', methods=['DELETE'])
def delete_meal(meal_id):
    m = Meal.query.get_or_404(meal_id)
    db.session.delete(m)
    db.session.commit()
    return jsonify({"message": "Meal deleted"})

def get_symptom_data_for_user(user_id):
    # Query all SymptomOutcome records for the user
    symptoms = SymptomOutcome.query.filter_by(user_id=user_id).all()
    # Convert to DataFrame
    symptom_data = pd.DataFrame([{
        'date': s.date.strftime('%Y-%m-%d'),
        'stoolConsistency': s.stool_consistency,
        'painPassingStool': s.pain_while_passing_stool,
        'stoolColor': s.stool_colour,
        'stoolFrequency': s.stool_frequency,
        'mucousInStool': s.mucous_in_stool,
        'bloodInStool': s.blood_in_stool,
        'painLocation': s.pain_location,
        'fever': s.fever,
        'nausea': s.nausea,
        'flatulence': s.flatulence
    } for s in symptoms])
    return symptom_data

def get_food_data_for_user(user_id):
    # Query all FoodIntake records for the user
    food_intakes = FoodIntake.query.filter_by(user_id=user_id).all()
    records = []
    for fi in food_intakes:
        # Get meals for this food intake
        meals = Meal.query.filter_by(food_intake_id=fi.id).all()
        meal_dict = {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []}
        for m in meals:
            if m.meal_type in meal_dict:
                meal_dict[m.meal_type].append(m.item)
        records.append({
            'date': fi.date.strftime('%Y-%m-%d'),
            'breakfast': ';'.join(meal_dict['breakfast']),
            'lunch': ';'.join(meal_dict['lunch']),
            'dinner': ';'.join(meal_dict['dinner']),
            'snacks': ';'.join(meal_dict['snacks']),
            'water': fi.water,
            'stressLevel': fi.stress
        })
    food_data = pd.DataFrame(records)
    return food_data

@app.route('/user_data/<int:user_id>', methods=['GET'])
def get_user_data(user_id):
    symptom_data = get_symptom_data_for_user(user_id)
    food_data = get_food_data_for_user(user_id)
    return jsonify({
        'symptom_data': symptom_data.to_dict(orient='records'),
        'food_data': food_data.to_dict(orient='records')
    })

@app.post('/login_user')
def user_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email:
        return jsonify({"error_message": "email is not provided"}), 400
    if not password:
        return jsonify({"error_message": "password is not provided"}), 400

    user = datastore.find_user(email=email)

    if not user:
        return jsonify({"error_message": "User was Not Found"}), 404
    
    if (user.active==False):
        return jsonify({"error_message": "You don't have access to the website"}), 401

    if check_password_hash(user.password, data.get("password")):
        # --- INITIALIZE VECTOR DB HERE ---
        from application.vector_db import create_vector_db
        food_data = get_food_data_for_user(user.id)
        symptom_data = get_symptom_data_for_user(user.id)
        if not food_data.empty and not symptom_data.empty:
            db, client, embed_fn = create_vector_db(food_data, symptom_data)
            user_vector_dbs[user.id] = (db, client, embed_fn)
        # --- END VECTOR DB INIT ---
        return jsonify({"name": user.name, "token": user.get_auth_token(), "email": user.email, "role": user.roles[0].name, "user_id": user.id, "active": user.active})
    else:
        return jsonify({"error_message": "Wrong Password"}), 400
    
'''def preprocess_symptom_data(symptom_data):
    cat_featf = ['Stool Colour', 'Pain location']
    num_featf = ['Stool consistency', 'Pain while passing stool', 'Stool frequency', 'Mucous in stool',
                 'Blood in stool', 'Fever', 'Nausea', 'Flatulence']
    pipef1 = Pipeline(steps=[('ord_enc', OrdinalEncoder(categories=[['brown', 'yellow', 'red'], ['Upper Abdomen', 'Lower Abdomen', 'Both',np.nan]])),
                             ('minmax_sc', MinMaxScaler())])
    pipef2 = Pipeline(steps=[('minmax_sc', MinMaxScaler())])
    ct = ColumnTransformer([('cat_featf', pipef1, cat_featf), ('num_featf', pipef2, num_featf)], remainder='passthrough')
    symptoms_ct = ct.fit_transform(symptom_data)
    symptoms_ct_df = pd.DataFrame(symptoms_ct)
 
    symptoms_final['date'] = symptoms_ct_df.iloc[:, -1]
    symptoms_final['Severity_score'] = symptoms_ct_df.iloc[:, :-1].sum(axis=1)
    return symptoms_final'''

@app.route('/trees_classifier/<int:user_id>', methods=['POST'])
def classify(user_id):
    if not user_id:
        return jsonify({'error': 'user_id required in request'}), 400

    # Fetch data from the database for this user
    symptoms = get_symptom_data_for_user(user_id)
    items = get_food_data_for_user(user_id)

    if symptoms.empty or items.empty:
        return jsonify({'error': 'No data found for this user.'}), 404

    # Make sure all expected columns exist and are in the correct format
    # (column names must match those used in the ML pipeline)
    # Symptoms columns: date, stoolConsistency, painPassingStool, stoolColor, stoolFrequency, mucousInStool, bloodInStool, painLocation, fever, nausea, flatulence
    # Food columns: date, breakfast, lunch, dinner, snacks, water, stressLevel

    # Making severity score
    cat_featf = ['stoolColor', 'painLocation']
    num_featf = ['stoolConsistency', 'painPassingStool', 'stoolFrequency', 'mucousInStool', 'bloodInStool', 'fever', 'nausea', 'flatulence']

    # Fill missing categorical values with 'None' string instead of np.nan
    for col in cat_featf:
        symptoms[col] = symptoms[col].fillna('None')  # Changed from np.nan to 'None'

    # Fill missing numeric values with 0
    for col in num_featf:
        symptoms[col] = pd.to_numeric(symptoms[col], errors='coerce').fillna(0)

    pipef1 = Pipeline(steps=[
        ('ord_enc', OrdinalEncoder(categories=[
            ['brown', 'yellow', 'red', 'None'],  # Added 'None' as category
            ['Upper Abdomen', 'Lower Abdomen', 'Both', 'None']  # Added 'None' as category
        ], handle_unknown='use_encoded_value', unknown_value=-1)),  # Added handling for unknown values
        ('minmax_sc', MinMaxScaler())
    ])
    pipef2 = Pipeline(steps=[('minmax_sc', MinMaxScaler())])
    ct = ColumnTransformer([
        ('cat_featf', pipef1, cat_featf),
        ('num_featf', pipef2, num_featf)
    ], remainder='passthrough')

    symptoms_ct = ct.fit_transform(symptoms[cat_featf + num_featf])
    symptoms_ct_df = pd.DataFrame(symptoms_ct, columns=cat_featf + num_featf)

    symptoms_final = pd.DataFrame()
    symptoms_final['date'] = symptoms['date']
    symptoms_final['Severity_score'] = symptoms_ct_df.sum(axis=1, skipna=True)

    # Food: combine all meals into one string per day
    items = items.fillna('')
    items['AllCombined'] = items[['breakfast', 'lunch', 'dinner', 'snacks']].agg(','.join, axis=1)
    items = items.applymap(lambda x: str(x).replace(';', ','))
    # Remove meal columns, keep AllCombined, water, stressLevel, date
    items = items.drop(['breakfast', 'lunch', 'dinner', 'snacks'], axis=1)

    # Merge food and symptoms on date
    merged_df = pd.merge(items, symptoms_final, left_on='date', right_on='date', how='inner')
    merged_df['Actual_Severity_Score'] = merged_df['Severity_score'].shift(-1)

    # Drop rows with missing Actual_Severity_Score
    merged_df = merged_df.dropna(subset=['Actual_Severity_Score'])

    # Drop unnecessary columns
    merged_df = merged_df.drop(['water', 'stressLevel', 'Severity_score', 'date'], axis=1, errors='ignore')

    # Determine trigger based on severity score
    threshold = 4
    merged_df['IsTrigger'] = (merged_df['Actual_Severity_Score'] > threshold).astype(int)

    # Prepare features and target for model
    features = merged_df[['AllCombined']]
    target = merged_df['IsTrigger']
    features_encoded = pd.concat([features, features['AllCombined'].str.get_dummies(sep=',')], axis=1).drop(columns=['AllCombined'])

    # Train the model
    model = ExtraTreesClassifier()
    model.fit(features_encoded, target)

    # Extract feature importances
    feature_importances = model.feature_importances_
    importance_df = pd.DataFrame({'Feature': features_encoded.columns, 'Importance': feature_importances})
    importance_df = importance_df.sort_values(by='Importance', ascending=False)

    # Return the JSON food importance
    return jsonify({'Food_trigger_score': importance_df.to_dict(orient='records')})

@app.route('/process_data/<int:user_id>', methods=['POST'])
def ask_rag(user_id):
    data = request.get_json()
    question = data.get('question')

    if not user_id or not question:
        return jsonify({'error': 'user_id and question are required'}), 400

    from main import user_vector_dbs
    if user_id not in user_vector_dbs:
        return jsonify({'error': 'Vector DB not initialized for this user.'}), 404

    db, client, embed_fn = user_vector_dbs[user_id]
    embed_fn.document_mode = False

    result = db.query(query_texts=[question], n_results=1)
    all_passages = result["documents"][0]

    query_oneline = question.replace("\n", " ")
    # In your endpoint, get conversation history from the request (client should send it)
    history = data.get('history', [])  # history = [{"role": "user", "content": ...}, {"role": "assistant", "content": ...}, ...]

    # Build the prompt with history
    prompt = "You are a helpful and informative medical bot for IBD patients.\n"
    for turn in history:
        if turn["role"] == "user":
            prompt += f"USER: {turn['content']}\n"
        else:
            prompt += f"BOT: {turn['content']}\n"
    prompt += f"USER: {question}\n"

    # Add passages as before...
    for passage in all_passages:
        passage_oneline = passage.replace("\n", " ")
        prompt += f"PASSAGE: {passage_oneline}\n"

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return jsonify({'answer': response.text})

@app.route('/user_visualizations/<int:user_id>', methods=['POST'])
def user_visualizations(user_id):
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    # Fetch symptom data
    symptoms = SymptomOutcome.query.filter_by(user_id=user_id).all()
    symptom_data = pd.DataFrame([{
        'date': s.date.strftime('%Y-%m-%d'),
        'stoolConsistency': s.stool_consistency,
        'painPassingStool': s.pain_while_passing_stool,
        'stoolColor': s.stool_colour,
        'stoolFrequency': s.stool_frequency,
        'mucousInStool': s.mucous_in_stool,
        'bloodInStool': s.blood_in_stool,
        'painLocation': s.pain_location,
        'fever': s.fever,
        'nausea': s.nausea,
        'flatulence': s.flatulence
    } for s in symptoms])

    # Fetch food data
    food_intakes = FoodIntake.query.filter_by(user_id=user_id).all()
    food_records = []
    for fi in food_intakes:
        meals = Meal.query.filter_by(food_intake_id=fi.id).all()
        meal_dict = {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []}
        for m in meals:
            if m.meal_type in meal_dict:
                meal_dict[m.meal_type].append(m.item)
        food_records.append({
            'date': fi.date.strftime('%Y-%m-%d'),
            'breakfast': ';'.join(meal_dict['breakfast']),
            'lunch': ';'.join(meal_dict['lunch']),
            'dinner': ';'.join(meal_dict['dinner']),
            'snacks': ';'.join(meal_dict['snacks']),
            'water': fi.water,
            'stressLevel': fi.stress
        })
    meal_data = pd.DataFrame(food_records)

    # Set up directories and userId
    userId = str(user_id)
    base_dir = '/home/parv/projects/ibdj2/frontend/graphs'
    os.makedirs(f"{base_dir}/stoolbar", exist_ok=True)
    os.makedirs(f"{base_dir}/stoolline", exist_ok=True)
    os.makedirs(f"{base_dir}/mealpie", exist_ok=True)
    os.makedirs(f"{base_dir}/stressscater", exist_ok=True)
    os.makedirs(f"{base_dir}/bloodbar", exist_ok=True)
    os.makedirs(f"{base_dir}/corr", exist_ok=True)
    os.makedirs(f"{base_dir}/freqbar", exist_ok=True)
    os.makedirs(f"{base_dir}/stressline", exist_ok=True)

    # 1. Distribution of Stool Colors
    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))
    sns.countplot(x='stoolColor', data=symptom_data)
    plt.title("Distribution of Stool Colors")
    plt.xlabel("Stool Color")
    plt.ylabel("Count")
    stoolbar_path = f"{base_dir}/stoolbar/{userId}.png"
    plt.savefig(stoolbar_path)
    plt.close()

    # 2. Stool Consistency Over Time
    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))
    plt.plot(symptom_data['date'], symptom_data['stoolConsistency'], marker='o')
    plt.xticks(rotation=45)
    plt.title("Stool Consistency Over Time")
    plt.xlabel("date")
    plt.ylabel("Stool Consistency")
    stoolline_path = f"{base_dir}/stoolline/{userId}.png"
    plt.savefig(stoolline_path)
    plt.close()

    # 3. Meal Pie Chart
    all_foods = meal_data[['breakfast', 'lunch', 'dinner', 'snacks']].apply(lambda x: ';'.join(x.dropna().astype(str)), axis=1)
    all_foods = ';'.join(all_foods).split(';')
    food_counts = pd.Series(all_foods).value_counts()
    plt.figure(figsize=(10, 6))
    food_counts.plot.pie(autopct='%1.1f%%')
    plt.title("Proportion of Different Food Items")
    mealpie_path = f"{base_dir}/mealpie/{userId}.png"
    plt.savefig(mealpie_path)
    plt.close()

    # 4. Scatter Stress vs Water
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='stressLevel', y='water', data=meal_data)
    plt.title("Scatter Plot: Stress vs. Water")
    stressscater_path = f"{base_dir}/stressscater/{userId}.png"
    plt.savefig(stressscater_path)
    plt.close()

    # 5. Distribution of Blood in Stool
    plt.figure(figsize=(10, 6))
    sns.countplot(x='bloodInStool', data=symptom_data)
    plt.title("Distribution of Blood in Stool")
    plt.xlabel("Presence of Blood")
    plt.ylabel("Count")
    bloodbar_path = f"{base_dir}/bloodbar/{userId}.png"
    plt.savefig(bloodbar_path)
    plt.close()

    # 6. Correlation Matrix for Symptom Data
    numeric_cols = symptom_data.select_dtypes(include='number')
    correlation_matrix = numeric_cols.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', square=True)
    plt.title("Correlation Matrix for Symptom Data")
    corr_path = f"{base_dir}/corr/{userId}.png"
    plt.savefig(corr_path)
    plt.close()

    # 7. Stool Frequency Over Time
    plt.figure(figsize=(10, 6))
    plt.plot(symptom_data['date'], symptom_data['stoolFrequency'], marker='o')
    plt.xticks(rotation=45)
    plt.title("Stool Frequency Over Time")
    plt.xlabel("date")
    plt.ylabel("Stool Frequency")
    freqbar_path = f"{base_dir}/freqbar/{userId}.png"
    plt.savefig(freqbar_path)
    plt.close()

    # 8. Stress Over Time
    plt.figure(figsize=(10, 6))
    plt.plot(meal_data['date'], meal_data['stressLevel'], marker='o')
    plt.xticks(rotation=45)
    plt.title("Stress Over Time")
    plt.xlabel("date")
    plt.ylabel("Stress Level")
    stressline_path = f"{base_dir}/stressline/{userId}.png"
    plt.savefig(stressline_path)
    plt.close()

    return jsonify({
        "stoolbar": stoolbar_path,
        "stoolline": stoolline_path,
        "mealpie": mealpie_path,
        "stressscater": stressscater_path,
        "bloodbar": bloodbar_path,
        "corr": corr_path,
        "freqbar": freqbar_path,
        "stressline": stressline_path
    })
