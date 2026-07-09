import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from database import db, User, CropPrediction, DiseaseHistory, ChatHistory
from ai_services import ai_manager

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()

DASHBOARD_STRINGS = {
    "en": {
        "welcome": "Welcome back",
        "assistant_title": "AI Assistant",
        "assistant_desc": "Chat with our intelligent bot for crop management and recommendations.",
        "disease_title": "Disease Detection",
        "disease_desc": "Upload plant photos to identify infections and calculate medicine dosages.",
        "market_title": "Market Rates",
        "market_desc": "Check live vegetable pricing metrics based on your regional district."
    },
    "ta": {
        "welcome": "நல்வரவு",
        "assistant_title": "AI உதவியாளர்",
        "assistant_desc": "பயிர் மேலாண்மை மற்றும் பரிந்துரைகளுக்கு எங்களது போட் உடன் உரையாடுங்கள்.",
        "disease_title": "நோய் கண்டறிதல்",
        "disease_desc": "பயிர் நோய்களைக் கண்டறிந்து மருந்து அளவைக் கணக்கிட புகைப்படங்களைப் பதிவேற்றவும்.",
        "market_title": "சந்தை விலைகள்",
        "market_desc": "உங்கள் மாவட்டத்தின் நேரடி காயறி விலை நிலவரங்களைச் சரிபார்க்கவும்."
    }
}

DISEASE_METADATA = {
    "Tomato_Bacterial_spot": {
        "en": {"name": "Tomato Bacterial Spot", "desc": "Bacterial Spot caused by Xanthomonas.", "symptoms": "Dark water-soaked spots on leaves.", "treatment": "Spray copper-based fungicides.", "pesticide": "Agrimycin-100 (Dosage: 2.0 ml/Litre)"},
        "ta": {"name": "தக்காளி பாக்டீரியா புள்ளி நோய்", "desc": "சாந்தோமோனாஸால் ஏற்படும் பாக்டீரியா இலைப்புள்ளி நோய்.", "symptoms": "இலைகளில் கரும் புள்ளிகள் தோன்றுதல்.", "treatment": "செம்பு சார்ந்த பூஞ்சைக் கொல்லிகளை தெளிக்கவும்.", "pesticide": "அக்ரிமைசின்-100 (அளவு: 2.0 மிமீ/லிட்டர்)"}
    },
    "Tomato_Early_blight": {
        "en": {"name": "Tomato Early Blight", "desc": "Fungal infection via Alternaria solani.", "symptoms": "Concentric rings on older leaves.", "treatment": "Apply protectant fungicides timely.", "pesticide": "Mancozeb 75% WP (Dosage: 2.5 grams/Litre)"},
        "ta": {"name": "தக்காளி ஆரம்பகால கருகல் நோய்", "desc": "ஆல்டர்நேரியா சோலனியால் ஏற்படும் ஆரம்பகால கருகல் நோய்.", "symptoms": "இலைகளில் வளைய வடிவ கரும்புள்ளிகள்.", "treatment": "மன்கோசெப் கொண்டு பயிர்களைத் தெளிக்கவும்.", "pesticide": "மன்கோசெப் 75% WP (அளவு: 2.5 கிராம்/லிட்டர்)"}
    },
    "Tomato_Late_blight": {
        "en": {"name": "Tomato Late Blight", "desc": "Caused by Phytophthora infestans.", "symptoms": "Dark patches on leaves with white mold underneath.", "treatment": "Deploy systemic fungicides instantly.", "pesticide": "Kavach (Dosage: 2.0 grams/Litre)"},
        "ta": {"name": "தக்காளி பின்கால கருகல் நோய்", "desc": "பைட்டோவ்ப்தோரா இன்ஃபெஸ்டான்ஸால் ஏற்படும் தீவிர பூஞ்சை நோய்.", "symptoms": "இலைகளில் பெரிய கரும் புள்ளிகள் மற்றும் வெள்ளை பூஞ்சை படலம்.", "treatment": "முறையான பூஞ்சைக் கொல்லிகளை உடனடியாகப் பயன்படுத்தவும்.", "pesticide": "கவச் (அளவு: 2.0 கிராம்/லிட்டர்)"}
    },
    "Tomato_Healthy": {
        "en": {"name": "Healthy Tomato Leaf", "desc": "No crop disease detected.", "symptoms": "None. Normal green pigmentation.", "treatment": "Maintain regular watering.", "pesticide": "No Chemical Treatment Required."},
        "ta": {"name": "ஆரோக்கியமான தக்காளி இலை", "desc": "பயிர் நோய் எதுவும் கண்டறியப்படவில்லை.", "symptoms": "எதுவும் இல்லை.", "treatment": "இயற்கை பராமரிப்பு முறைகளை தொடரவும்.", "pesticide": "இரசாயன மருந்துகள் தேவையில்லை."}
    }
}

MARKET_DATA = {
    "Karur": {
        "Tomato (தக்காளி)": {"min": 22, "max": 28, "avg": 25},
        "Onion (வெங்காயம்)": {"min": 38, "max": 46, "avg": 42},
        "Potato (உருளைக்கிழங்கு)": {"min": 26, "max": 32, "avg": 29},
        "Brinjal (கத்தரிக்காய்)": {"min": 30, "max": 40, "avg": 35},
        "Drumstick (முருங்கைக்காய்)": {"min": 45, "max": 60, "avg": 52}
    },
    "Trichy": {
        "Tomato (தக்காளி)": {"min": 19, "max": 24, "avg": 21},
        "Onion (வெங்காயம்)": {"min": 34, "max": 42, "avg": 38},
        "Potato (உருளைக்கிழங்கு)": {"min": 23, "max": 29, "avg": 26},
        "Brinjal (கத்தரிக்காய்)": {"min": 26, "max": 34, "avg": 30},
        "Drumstick (முருங்கைக்காய்)": {"min": 52, "max": 68, "avg": 60}
    },
    "Madurai": {
        "Tomato (தக்காளி)": {"min": 25, "max": 32, "avg": 28},
        "Onion (வெங்காயம்)": {"min": 42, "max": 52, "avg": 47},
        "Potato (உருளைக்கிழங்கு)": {"min": 29, "max": 36, "avg": 32},
        "Brinjal (கத்தரிக்காய்)": {"min": 34, "max": 44, "avg": 39},
        "Drumstick (முருங்கைக்காய்)": {"min": 41, "max": 54, "avg": 47}
    },
    "Coimbatore": {
        "Tomato (தக்காளி)": {"min": 17, "max": 23, "avg": 20},
        "Onion (வெங்காயம்)": {"min": 32, "max": 40, "avg": 36},
        "Potato (உருளைக்கிழங்கு)": {"min": 24, "max": 30, "avg": 27},
        "Brinjal (கத்தரிக்காய்)": {"min": 23, "max": 31, "avg": 27},
        "Drumstick (முருங்கைக்காய்)": {"min": 46, "max": 58, "avg": 52}
    },
    "Chennai": {
        "Tomato (தக்காளி)": {"min": 28, "max": 36, "avg": 32},
        "Onion (வெங்காயம்)": {"min": 45, "max": 56, "avg": 50},
        "Potato (உருளைக்கிழங்கு)": {"min": 32, "max": 40, "avg": 36},
        "Brinjal (கத்தரிக்காய்)": {"min": 38, "max": 50, "avg": 44},
        "Drumstick (முருங்கைக்காய்)": {"min": 65, "max": 85, "avg": 75}
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        if db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none():
            flash('Username already registered.', 'danger')
            return render_template('register.html')
            
        hashed_password = generate_password_hash(request.form.get('password'), method='scrypt')
        new_user = User(
            fullname=request.form.get('fullname'), username=username, email=email,
            mobile=request.form.get('mobile'), password_hash=hashed_password,
            district=request.form.get('district', 'Karur'), state=request.form.get('state'),
            language=request.form.get('language', 'en'), farm_size=float(request.form.get('farm_size', 1.0))
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        user = db.session.execute(db.select(User).filter((User.username == u) | (User.email == u))).scalar_one_or_none()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user)
            session['lang'] = user.language
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    lang = session.get('lang', current_user.language or 'en')
    strings = DASHBOARD_STRINGS.get(lang, DASHBOARD_STRINGS['en'])
    return render_template('dashboard.html', lang=lang, strings=strings)

@app.route('/ai_assistant', methods=['GET', 'POST'])
@login_required
def ai_assistant():
    lang = session.get('lang', current_user.language or 'en')
    if request.method == 'POST':
        data = request.get_json() or {}
        user_msg = data.get('message', '')
        
        if "recommend crop" in user_msg.lower() or "பரிந்துரை" in user_msg:
            user_msg += f" (Context -> District: {current_user.district}, Farm: {current_user.farm_size} acres.)"

        db.session.add(ChatHistory(user_id=current_user.id, role='user', message=user_msg, language=lang))
        db.session.commit()
        
        history = db.session.execute(db.select(ChatHistory).filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.asc())).scalars().all()
        ai_response = ai_manager.consult_llm_agronomist(history, user_msg, language=lang)
        
        db.session.add(ChatHistory(user_id=current_user.id, role='model', message=ai_response, language=lang))
        db.session.commit()
        return jsonify({'response': ai_response})
        
    return render_template('ai_assistant.html', conversation=db.session.execute(db.select(ChatHistory).filter_by(user_id=current_user.id)).scalars().all(), lang=lang)

@app.route('/disease_detection', methods=['GET', 'POST'])
@login_required
def disease_detection():
    lang = session.get('lang', current_user.language or 'en')
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Calling the updated live AI vision analyzer passing the session context language
            ai_result = ai_manager.analyze_plant_disease_with_ai(file_path, language=lang)
            
            return render_template(
                'disease_results.html', 
                disease=ai_result['name'], 
                meta=ai_result, 
                confidence=ai_result['confidence'], 
                img_name=filename, 
                lang=lang
            )
    return render_template('disease_detection.html', lang=lang)

@app.route('/market_rates', methods=['GET', 'POST'])
@login_required
def market_rates():
    lang = session.get('lang', current_user.language or 'en')
    selected_district = request.form.get('district', current_user.district)
    if selected_district not in MARKET_DATA:
        selected_district = "Karur"
        
    rates = MARKET_DATA[selected_district]
    return render_template('market_rates.html', rates=rates, selected_district=selected_district, lang=lang, districts=MARKET_DATA.keys())

@app.route('/toggle_lang_ajax', methods=['POST'])
@login_required
def toggle_lang_ajax():
    data = request.get_json() or {}
    target_lang = data.get('lang', 'en')
    
    # Securely force language variables across memory structures
    session['lang'] = target_lang
    current_user.language = target_lang
    db.session.commit()
    
    return jsonify({'status': 'success', 'current_lang': target_lang})

@app.route('/logout')
def logout():
    logout_user(); session.clear(); return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5002)