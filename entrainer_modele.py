# Script pour entraîner le modèle météo Long Terme pour Rabat
import pandas as pd
import numpy as np
import requests
import joblib
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

print("🌤️ Entraînement du modèle météo Long Terme - Rabat")
print("=" * 50)

# 1. Récupération des données historiques (3 mois)
print("\n📥 Téléchargement des données historiques (3 mois)...")

# Dates pour les 3 derniers mois
end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 34.0209,
    "longitude": -6.8416,
    "start_date": start_date,
    "end_date": end_date,
    "hourly": "temperature_2m",
    "timezone": "GMT"
}

response = requests.get(url, params=params)
data = response.json()

print(f"✅ Données récupérées du {start_date} au {end_date}")

# 2. Préparation des données
print("\n🔧 Préparation des données...")

df = pd.DataFrame({
    'date': pd.to_datetime(data['hourly']['time']),
    'temperature': data['hourly']['temperature_2m']
})

# Création des features
df['jour_annee'] = df['date'].dt.dayofyear
df['mois'] = df['date'].dt.month
df['heure'] = df['date'].dt.hour

# Encodage cyclique (Sin/Cos) pour capturer la saisonnalité
df['day_cos'] = np.cos(2 * np.pi * df['jour_annee'] / 365.25)
df['day_sin'] = np.sin(2 * np.pi * df['jour_annee'] / 365.25)

# Suppression des valeurs nulles
df = df.dropna()

print(f"✅ {len(df)} observations préparées")

# 3. Entraînement du modèle
print("\n🧠 Entraînement du modèle Random Forest...")

features = ['day_cos', 'day_sin', 'heure', 'mois']
X = df[features]
y = df['temperature']

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)

model.fit(X, y)

print("✅ Modèle entraîné avec succès!")

# 4. Sauvegarde du modèle
print("\n💾 Sauvegarde du modèle...")
joblib.dump(model, 'cerveau_meteo_long_terme.pkl')
print("✅ Modèle sauvegardé: cerveau_meteo_long_terme.pkl")

# 5. Test rapide
print("\n🧪 Test du modèle...")
test_data = pd.DataFrame({
    'jour_annee': [datetime.now().timetuple().tm_yday],
    'mois': [datetime.now().month],
    'heure': [14]
})
test_data['day_cos'] = np.cos(2 * np.pi * test_data['jour_annee'] / 365.25)
test_data['day_sin'] = np.sin(2 * np.pi * test_data['jour_annee'] / 365.25)

prediction = model.predict(test_data[features])[0]
print(f"🌡️ Prédiction pour aujourd'hui à 14h: {prediction:.1f}°C")

print("\n" + "=" * 50)
print("✅ TERMINÉ! Vous pouvez maintenant relancer app_meteo.py")
