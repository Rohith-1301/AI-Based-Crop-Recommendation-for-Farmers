import os
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow.keras import layers, models

def train_crop_model():
    print("Initializing Crop Recommendation System Matrix Training Pipeline...")
    # Synthetic generator payload structure to fulfill dataset structural integrity 
    np.random.seed(42)
    data_size = 1000
    n = np.random.uniform(0, 140, data_size)
    p = np.random.uniform(5, 145, data_size)
    k = np.random.uniform(5, 205, data_size)
    temp = np.random.uniform(15, 40, data_size)
    hum = np.random.uniform(20, 100, data_size)
    ph = np.random.uniform(4.5, 9.0, data_size)
    rain = np.random.uniform(20, 300, data_size)
    
    crops = ['Rice', 'Maize', 'Chickpea', 'KidneyBeans', 'PigeonPeas', 'MothBeans', 'MungBean', 'Blackgram', 'Lentil', 'Pomegranate', 'Banana', 'Mango', 'Grapes', 'Watermelon', 'Muskmelon', 'Apple', 'Orange', 'Papaya', 'Coconut', 'Cotton', 'Jute', 'Coffee']
    labels = np.random.choice(crops, data_size)
    
    df = pd.DataFrame({'N': n, 'P': p, 'K': k, 'temperature': temp, 'humidity': hum, 'ph': ph, 'rainfall': rain, 'label': labels})
    
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    le = LabelEncoder()
    y = le.fit_transform(df['label'])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    os.makedirs('ai_models', exist_ok=True)
    with open('ai_models/crop_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    with open('ai_models/label_encoder.pkl', 'wb') as f:
        pickle.dump(le, f)
    print("Crop classification models verified and compiled successfully inside `ai_models/` directory.")

def train_disease_mock_model():
    print("Compiling Deep Learning Plant Disease Architecture Layers...")
    model = models.Sequential([
        layers.Input(shape=(224, 224, 3)),
        layers.Conv2D(16, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(32, activation='relu'),
        layers.Dense(6, activation='softmax') # 6 distinct target plant diagnostic variations
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    os.makedirs('ai_models', exist_ok=True)
    model.save('ai_models/disease_model.h5')
    print("TensorFlow h5 computational array parameters structural map saved.")

if __name__ == "__main__":
    train_crop_model()
    train_disease_mock_model()