# app_meteo.py - Application Météo avec IA
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests
import base64
from PIL import Image
from datetime import datetime, timedelta

# --- FONCTION POUR DÉTERMINER LA SAISON ---
def get_season(month, day):
    """Retourne la saison et sa couleur selon le mois et le jour"""
    if (month == 12 and day >= 21) or month in [1, 2] or (month == 3 and day < 20):
        return "Hiver", "🔵", "#ADD8E6"  # Bleu clair
    elif (month == 3 and day >= 20) or month in [4, 5] or (month == 6 and day < 21):
        return "Printemps", "🌸", "#FFB6C1"  # Rose
    elif (month == 6 and day >= 21) or month in [7, 8] or (month == 9 and day < 23):
        return "Été", "☀️", "#FFD700"  # Jaune doré
    else:
        return "Automne", "🍂", "#FF8C00"  # Orange

# --- 1. CHARGEMENT DU LOGO ---
try:
    logo_img = Image.open("meteo.jpg")
except FileNotFoundError:
    logo_img = "🌤️"

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Météo IA Rabat",
    page_icon=logo_img,
    layout="wide"
)

# --- 3. INJECTION DES ICÔNES POUR TÉLÉPHONE (PWA) ---
try:
    with open("apple-touch-icon.png", "rb") as f:
        apple_icon = base64.b64encode(f.read()).decode()
    
    st.markdown(f'''
        <link rel="apple-touch-icon" href="data:image/png;base64,{apple_icon}">
        <link rel="icon" type="image/png" sizes="192x192" href="data:image/png;base64,{apple_icon}">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <meta name="apple-mobile-web-app-title" content="Météo Rabat">
    ''', unsafe_allow_html=True)
except:
    pass

st.title("🌤️ Application Météo IA - Rabat")

# --- SECTION PRÉVISIONS ---
st.markdown("---")

# Sélecteurs
col_jours, col_heure = st.columns(2)

with col_jours:
    nb_jours = st.slider("📆 Nombre de jours de prévision", min_value=1, max_value=30, value=7, step=1)

with col_heure:
    heure_selectionnee = st.number_input("🕐 Heure de la journée", min_value=0, max_value=23, value=14, step=1)
    st.caption("Utilisez les flèches ⬆️⬇️ pour changer l'heure")

st.subheader(f"📅 Prévisions pour les {nb_jours} prochains jours à {heure_selectionnee}h")

# Chargement des modèles et données historiques
try:
    model_path = 'cerveau_meteo_long_terme.pkl'
    model_data = joblib.load(model_path)
    
    # Extraction des modèles
    if isinstance(model_data, dict):
        model_temp = model_data.get('model_temp')
        model_humidity = model_data.get('model_humidity')
        features = model_data.get('features')
        historical_data = model_data.get('historical_data')
    else:
        st.error("❌ Format de modèle non compatible. Veuillez réentraîner le modèle.")
        st.stop()
    
    # Génération des prévisions
    start_date = pd.Timestamp.now().normalize() + pd.Timedelta(days=1)
    dates_semaine = pd.date_range(start=start_date, periods=nb_jours, freq='D')
    
    df_semaine = pd.DataFrame({'date': dates_semaine})
    df_semaine['jour_annee'] = df_semaine['date'].dt.dayofyear
    df_semaine['mois'] = df_semaine['date'].dt.month
    df_semaine['jour'] = df_semaine['date'].dt.day
    df_semaine['heure'] = heure_selectionnee
    
    # Encodage cyclique
    df_semaine['day_cos'] = np.cos(2 * np.pi * df_semaine['jour_annee'] / 365.25)
    df_semaine['day_sin'] = np.sin(2 * np.pi * df_semaine['jour_annee'] / 365.25)
    df_semaine['hour_cos'] = np.cos(2 * np.pi * df_semaine['heure'] / 24)
    df_semaine['hour_sin'] = np.sin(2 * np.pi * df_semaine['heure'] / 24)
    df_semaine['month_cos'] = np.cos(2 * np.pi * df_semaine['mois'] / 12)
    df_semaine['month_sin'] = np.sin(2 * np.pi * df_semaine['mois'] / 12)
    
    # Prédictions
    df_semaine['Prediction_Temp'] = model_temp.predict(df_semaine[features])
    df_semaine['Prediction_Humidity'] = model_humidity.predict(df_semaine[features])
    
    # Ajout des saisons
    df_semaine['Saison'], df_semaine['Icone_Saison'], df_semaine['Couleur_Saison'] = zip(*df_semaine.apply(
        lambda row: get_season(row['mois'], row['jour']), axis=1
    ))
    
    # Noms des jours en français
    jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    
    # Affichage du tableau avec saisons
    df_affichage = df_semaine.copy()
    df_affichage['Jour'] = df_affichage['date'].dt.dayofweek.map(lambda x: jours_fr[x])
    df_affichage['Date'] = df_affichage['date'].dt.strftime('%d/%m')
    df_affichage['Saison_Display'] = df_affichage['Icone_Saison'] + ' ' + df_affichage['Saison']
    df_affichage['Température'] = df_affichage['Prediction_Temp'].round(1).astype(str) + '°C'
    df_affichage['💧 Humidité'] = df_affichage['Prediction_Humidity'].round(0).astype(int).astype(str) + '%'
    
    # Création du tableau final
    df_display = df_affichage[['Jour', 'Date', 'Saison_Display', 'Température', '💧 Humidité']].copy()
    df_display.columns = ['Jour', 'Date', 'Saison', 'Température', '💧 Humidité']
    
    # Affichage avec sélection de ligne
    st.write("### 📊 Tableau des prévisions (Cliquez sur une ligne pour voir l'historique)")
    
    # Utiliser st.dataframe avec on_select
    event = st.dataframe(
        df_display,
        hide_index=True,
        width="stretch",
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # Affichage de l'historique si une ligne est sélectionnée
    if event.selection and len(event.selection.rows) > 0:
        selected_row = event.selection.rows[0]
        selected_date = dates_semaine[selected_row]
        selected_month = selected_date.month
        selected_day = selected_date.day
        
        st.markdown("---")
        st.write(f"### 📜 Historique pour le {selected_day:02d}/{selected_month:02d} à {heure_selectionnee}h")
        
        if historical_data is not None:
            # Filtrer les données historiques pour cette date et heure
            hist_filtered = historical_data[
                (historical_data['date'].dt.month == selected_month) &
                (historical_data['date'].dt.day == selected_day) &
                (historical_data['date'].dt.hour == heure_selectionnee)
            ].copy()
            
            if len(hist_filtered) > 0:
                # Afficher les 5 dernières années
                hist_filtered['Année'] = hist_filtered['date'].dt.year
                hist_filtered = hist_filtered.sort_values('Année', ascending=False).head(5)
                
                hist_display = hist_filtered[['Année', 'temperature', 'humidity']].copy()
                hist_display.columns = ['Année', '🌡️ Température (°C)', '💧 Humidité (%)']
                hist_display['🌡️ Température (°C)'] = hist_display['🌡️ Température (°C)'].round(1)
                hist_display['💧 Humidité (%)'] = hist_display['💧 Humidité (%)'].round(0).astype(int)
                
                st.dataframe(hist_display, hide_index=True, width="stretch")
                
                # Graphique de l'évolution
                st.line_chart(hist_display.set_index('Année')[['🌡️ Température (°C)', '💧 Humidité (%)']])
            else:
                st.info("Aucune donnée historique disponible pour cette date.")
        else:
            st.warning("Les données historiques ne sont pas disponibles. Réentraînez le modèle.")
    
    # Graphique de comparaison (colonne droite)
    st.markdown("---")
    st.write("### 📈 Graphique des prévisions sur la période")
    
    chart_data = df_semaine.set_index('date')[['Prediction_Temp', 'Prediction_Humidity']]
    chart_data.columns = ['Température (°C)', 'Humidité (%)']
    st.line_chart(chart_data)

except FileNotFoundError:
    st.error(f"❌ Fichier modèle introuvable : '{model_path}'. Veuillez relancer le notebook d'entraînement.")
except Exception as e:
    st.error(f"Erreur lors de la prédiction : {e}")
    st.exception(e)
