import streamlit as st
from database import get_patients
import pandas as pd

if "user" not in st.session_state:
    st.warning("Veuillez vous connecter")
    st.stop()

st.title("Recherche patient")

data = get_patients()

if not data:
    st.info("Aucun patient dans la base de données. Importez un fichier CSV depuis Import / Export.")
    st.stop()

df = pd.DataFrame(data, columns=[
    "ID", "Prénom", "Nom", "Age", "Genre", "Département", "Temps Attente", "Priorité"
])

# =========================================
# RECHERCHE
# =========================================

st.subheader("Rechercher un patient")

col1, col2 = st.columns(2)

with col1:
    search = st.text_input("Nom ou prénom", placeholder="Ex: EL KAMILI, Wijdane...")

with col2:
    search_id = st.number_input("Rechercher par ID", min_value=0, step=1, value=0)

st.markdown("---")

# =========================================
# FILTRES
# =========================================

st.subheader("Filtres avancés")

col1, col2, col3 = st.columns(3)

with col1:
    priorites = ["Toutes"] + sorted(df["Priorité"].dropna().unique().tolist())
    filtre_priorite = st.selectbox("Priorité", priorites)

with col2:
    departements = ["Tous"] + sorted(df["Département"].dropna().unique().tolist())
    filtre_dept = st.selectbox("Département", departements)

with col3:
    genres = ["Tous"] + sorted(df["Genre"].dropna().unique().tolist())
    filtre_genre = st.selectbox("Genre", genres)

# Slider Age — corrigé
age_min_data = int(df["Age"].min())
age_max_data = int(df["Age"].max())

if age_min_data < age_max_data:
    age_min, age_max = st.slider(
        "Tranche d'âge",
        min_value=age_min_data,
        max_value=age_max_data,
        value=(age_min_data, age_max_data)
    )
else:
    age_min, age_max = age_min_data, age_max_data
    st.info(f"Age des patients : {age_min_data} ans")

# Slider Temps Attente — corrigé
attente_min_data = int(df["Temps Attente"].min())
attente_max_data = int(df["Temps Attente"].max())

if df["Temps Attente"].sum() > 0 and attente_min_data < attente_max_data:
    attente_min, attente_max = st.slider(
        "Temps d'attente (min)",
        min_value=attente_min_data,
        max_value=attente_max_data,
        value=(attente_min_data, attente_max_data)
    )
else:
    attente_min, attente_max = attente_min_data, attente_max_data

st.markdown("---")

# =========================================
# APPLICATION DES FILTRES
# =========================================

df_result = df.copy()

if search:
    df_result = df_result[
        df_result["Prénom"].str.contains(search, case=False, na=False) |
        df_result["Nom"].str.contains(search, case=False, na=False)
    ]

if search_id > 0:
    df_result = df_result[df_result["ID"] == search_id]

if filtre_priorite != "Toutes":
    df_result = df_result[df_result["Priorité"] == filtre_priorite]

if filtre_dept != "Tous":
    df_result = df_result[df_result["Département"] == filtre_dept]

if filtre_genre != "Tous":
    df_result = df_result[df_result["Genre"] == filtre_genre]

df_result = df_result[
    (df_result["Age"] >= age_min) &
    (df_result["Age"] <= age_max)
]

if df["Temps Attente"].sum() > 0:
    df_result = df_result[
        (df_result["Temps Attente"] >= attente_min) &
        (df_result["Temps Attente"] <= attente_max)
    ]

st.markdown("---")

# =========================================
# RÉSULTATS
# =========================================

st.subheader("Résultats")

if df_result.empty:
    st.warning("Aucun patient trouvé.")
else:
    st.success(f"{len(df_result)} patient(s) trouvé(s)")
    st.dataframe(df_result, use_container_width=True)

    csv = df_result.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Télécharger les résultats (CSV)",
        data=csv,
        file_name="resultats_recherche.csv",
        mime="text/csv"
    )