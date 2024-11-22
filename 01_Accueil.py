import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta
import calendar
from collections import defaultdict
import html

def setup_page():
    st.set_page_config(
        page_title="K.E.R",
        page_icon="🖤",
        layout="wide"
    )
    
    # Schéma de couleurs
    COLORS = {
        "orange": "#FF6B35",
        "blue": "#2EC4B6",
        "gray": "#262626",
        "white": "#FFFFFF",
        "light_gray": "#f8f9fa",
        "highlight": "#FFE5D9"
    }
    
    # CSS personnalisé
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {COLORS["white"]};
            color: {COLORS["gray"]};
        }}
        .week-container {{
            background-color: {COLORS["light_gray"]};
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }}
        .current-week {{
            background-color: {COLORS["highlight"]};
            border-left: 5px solid {COLORS["orange"]};
        }}
        .day-header {{
            font-size: 1rem;
            font-weight: bold;
            padding: 0.5rem;
            text-align: center;
            color: {COLORS["blue"]};
            border-bottom: 2px solid {COLORS["blue"]};
        }}
        .day-column {{
            background-color: white;
            padding: 0.5rem;
            border-radius: 5px;
            height: 100%;
            min-height: 200px;
        }}
        .event-card {{
            background-color: {COLORS["highlight"]};
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            border: 1px solid {COLORS["orange"]};
            font-size: 0.9rem;
        }}
        .event-time {{
            color: {COLORS["orange"]};
            font-weight: bold;
            font-size: 0.9rem;
        }}
        .upcoming-event-card {{
            background-color: white;
            padding: 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            border: 1px solid #eee;
        }}
        </style>
    """, unsafe_allow_html=True)

    # CSS personnalisé avec styles pour le tooltip
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {COLORS["white"]};
            color: {COLORS["gray"]};
        }}
        .week-container {{
            background-color: {COLORS["light_gray"]};
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }}
        .day-header {{
            font-size: 1rem;
            font-weight: bold;
            padding: 0.5rem;
            text-align: center;
            color: {COLORS["blue"]};
            border-bottom: 2px solid {COLORS["blue"]};
        }}
        .day-column {{
            background-color: white;
            padding: 0.5rem;
            border-radius: 5px;
            height: 100%;
            min-height: 200px;
        }}
        .event-card {{
            background-color: {COLORS["highlight"]};
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            border: 1px solid {COLORS["orange"]};
            font-size: 0.9rem;
            position: relative;
            cursor: pointer;
        }}
        .event-card:hover {{
            background-color: {COLORS["orange"]};
            color: white;
        }}
        .event-time {{
            color: {COLORS["orange"]};
            font-weight: bold;
            font-size: 0.9rem;
        }}
        .upcoming-event-card {{
            background-color: white;
            padding: 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            border: 1px solid #eee;
        }}
        /* Styles pour le tooltip */
        .tooltip {{
            position: relative;
            display: inline-block;
        }}
        .tooltip .tooltip-content {{
            visibility: hidden;
            background-color: #333;
            color: #fff;
            text-align: left;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            width: 300px;
            left: 50%;
            transform: translateX(-50%);
            bottom: 100%;
            margin-bottom: 5px;
            opacity: 0;
            transition: opacity 0.3s;
        }}
        .tooltip:hover .tooltip-content {{
            visibility: visible;
            opacity: 1;
        }}
        .tooltip .tooltip-content::after {{
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #333 transparent transparent transparent;
        }}
        </style>
    """, unsafe_allow_html=True)



def load_data():
    """Charger et prétraiter les données depuis Google Sheets"""
    conn = st.connection("gsheets", type=GSheetsConnection)
    data = conn.read(worksheet='db')
    data['Date de l\'événement'] = pd.to_datetime(data['Date de l\'événement'], format='%d/%m/%Y')
    return data

def get_week_date_range(date):
    """Obtenir le début et la fin de la semaine pour une date donnée"""
    start_of_week = date - timedelta(days=date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def create_sidebar():
    """Créer la barre latérale"""
    st.sidebar.image("media/logo_ker.png", width=300)
    
    st.sidebar.header("💓 Raison d'être")
    st.sidebar.markdown("""
    **Notre mission 🎯**
    Recenser et centraliser tous les évènements associatifs, 
    sportifs et culturels des Côtes d'Armor !
    
    **Pourquoi faire ❓**
    - Ne plus rater aucun évènement 😤
    - Permettre aux évènements de trouver leurs publics 🙌
    """)
    
    st.sidebar.header("🥳 Besoin de planifier un évènement ?")
    st.sidebar.markdown("""
    👉 [C'est par ici !](https://docs.google.com/forms/d/e/1FAIpQLSfDONZ2gbxo7yDDUcSTz51Hvbc_IgDrxk8TlXW-pgT7TbVgpw/viewform)
    """)
    
    st.sidebar.header("👍 Ne manquez plus aucune actualité !")
    st.sidebar.markdown("""
    - [X](https://x.com/Alex_mnds)
    - [Instagram](https://www.instagram.com/)
    - [Facebook](https://www.facebook.com/)
    """)

def create_filters(df):
    """Créer les filtres pour les événements"""
    col1, col2 = st.columns(2)
    
    with col1:
        categories = df['Catégorie de l\'évènement'].unique()
        selected_category = st.multiselect(
            "Catégories",
            options=categories,
            default=categories
        )
    
    with col2:
        search_term = st.text_input("Rechercher un événement", "")
    
    return selected_category, search_term

def filter_events(df, selected_category, search_term):
    """Filtrer les événements selon les critères"""
    filtered_df = df[df['Catégorie de l\'évènement'].isin(selected_category)]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['Nom de l\'évènement'].str.contains(search_term, case=False) |
            filtered_df['Description de l\'évènement'].str.contains(search_term, case=False)
        ]
    
    return filtered_df

def display_event_in_day(event):
    """Afficher un événement dans la colonne du jour"""
    st.markdown(f"""
    <div class="event-card">
        <div class="event-time">{event['Nom de l\'évènement']}</div>
        <div>🏢 {event['Nom de l\'entreprise ou de l\'association'][:30]}...</div>
        <div>📍 {event['Code postal de l\'évènement']}</div>
    </div>
    """, unsafe_allow_html=True)

def create_tooltip_content(event):
    """Créer le contenu HTML de l'infobulle"""
    return f"""
    <div>
        <strong>{event['Nom de l\'évènement']}</strong><br>
        🏢 {event['Nom de l\'entreprise ou de l\'association']}<br>
        📍 {event['Code postal de l\'évènement']}<br>
        <strong>Catégorie:</strong> {event['Catégorie de l\'évènement']}<br>
        <br>
        {event['Description de l\'évènement']}<br>
        {f"<strong>Média(s):</strong> {event['Média(s)']}" if pd.notna(event['Média(s)']) else ""}
    </div>
    """

def display_event_in_day(event):
    """Afficher un événement dans la colonne du jour avec une infobulle"""
    tooltip_content = create_tooltip_content(event)
    
    # Échapper les caractères spéciaux dans le contenu HTML
    escaped_tooltip = html.escape(tooltip_content)
    
    st.markdown(f"""
    <div class="tooltip">
        <div class="event-card">
            <div class="event-time">{event['Nom de l\'évènement'][:30]}...</div>
        </div>
        <div class="tooltip-content">
            {tooltip_content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_upcoming_event(event):
    """Afficher un événement à venir"""
    st.markdown(f"""
    <div class="upcoming-event-card">
        <div class="event-time">{event['Nom de l\'évènement']}</div>
        <div>📍 {event['Code postal de l\'évènement']} | 🏢 {event['Nom de l\'entreprise ou de l\'association']}</div>
        <div><strong>Catégorie:</strong> {event['Catégorie de l\'évènement']}</div>
        <div>{event['Description de l\'évènement']}</div>
        {f"<div><strong>Média(s):</strong> {event['Média(s)']}</div>" if pd.notna(event['Média(s)']) else ""}
    </div>
    """, unsafe_allow_html=True)

def display_current_week(week_events, week_start):
    """Afficher la semaine en cours avec les jours côte à côte"""
    st.header("📅 Cette semaine")
    
    # Créer une colonne pour chaque jour
    cols = st.columns(7)
    
    # Afficher chaque jour
    for i, col in enumerate(cols):
        current_date = week_start + timedelta(days=i)
        with col:
            # En-tête du jour
            st.markdown(f"""
            <div class="day-header">
                {calendar.day_name[current_date.weekday()][:3]}<br>
                {current_date.strftime('%d/%m')}
            </div>
            """, unsafe_allow_html=True)
            
            # Conteneur pour les événements du jour
            with st.container():
                st.markdown('<div class="day-column">', unsafe_allow_html=True)
                if current_date in week_events:
                    for event in week_events[current_date]:
                        display_event_in_day(event)
                st.markdown('</div>', unsafe_allow_html=True)

def display_upcoming_events(df, current_week_end):
    """Afficher les événements à venir après la semaine en cours"""
    st.header("📆 Prochains événements")
    
    upcoming_events = df[df['Date de l\'événement'].dt.date > current_week_end]
    if not upcoming_events.empty:
        for _, event in upcoming_events.iterrows():
            display_upcoming_event(event)
    else:
        st.info("Aucun événement à venir pour le moment")

def main():
    setup_page()
    st.title("K.E.R - Agenda des événements")
    
    # Charger les données
    data = load_data()
    
    # Créer la barre latérale
    create_sidebar()
    
    # Créer les filtres
    selected_category, search_term = create_filters(data)
    
    # Filtrer les événements
    filtered_df = filter_events(data, selected_category, search_term)
    
    # Obtenir la semaine en cours
    today = datetime.now().date()
    current_week_start, current_week_end = get_week_date_range(today)
    
    # Grouper les événements de la semaine par jour
    week_events = defaultdict(list)
    current_week_df = filtered_df[
        (filtered_df['Date de l\'événement'].dt.date >= current_week_start) &
        (filtered_df['Date de l\'événement'].dt.date <= current_week_end)
    ]
    
    for _, event in current_week_df.iterrows():
        week_events[event['Date de l\'événement'].date()].append(event)
    
    # Afficher la semaine en cours
    display_current_week(week_events, current_week_start)
    
    # Afficher les événements à venir
    display_upcoming_events(filtered_df, current_week_end)

if __name__ == "__main__":
    main()