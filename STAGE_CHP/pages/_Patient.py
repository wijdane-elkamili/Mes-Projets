import streamlit as st
from database import get_patients, delete_patient
import pandas as pd

if "user" not in st.session_state:
    st.warning("Veuillez vous connecter")
    st.stop()

st.title("Liste des patients")

data = get_patients()

if not data:
    st.info("Aucun patient dans la base de données. Importez un fichier CSV depuis Import / Export.")
    st.stop()

df = pd.DataFrame(data, columns=[
    "ID", "Prénom", "Nom", "Age", "Genre", "Département", "Temps Attente", "Priorité"
])

# =========================================
# MÉTRIQUES
# =========================================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total patients", len(df))
col2.metric("Critiques", len(df[df["Priorité"] == "P1"]))
col3.metric("Urgents", len(df[df["Priorité"] == "P2"]))
attente = df['Temps Attente'].mean()
col4.metric("Attente moyenne", f"{round(attente, 1)} min" if attente > 0 else "Non renseigné")
st.markdown("---")

# =========================================
# FILTRES
# =========================================

st.subheader("Filtres")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    filtre_priorite = st.selectbox(
        "Priorité",
        ["Toutes", "P1", "P2", "P3", "P4", "Critique", "Urgent", "Normal"]
    )

with col_f2:
    departements = ["Tous"] + sorted(df["Département"].dropna().unique().tolist())
    filtre_dept = st.selectbox("Département", departements)

with col_f3:
    filtre_genre = st.selectbox("Genre", ["Tous", "Homme", "Femme"])

recherche = st.text_input("Rechercher par nom ou prénom")

# Application des filtres
df_filtre = df.copy()

if filtre_priorite != "Toutes":
    df_filtre = df_filtre[df_filtre["Priorité"] == filtre_priorite]

if filtre_dept != "Tous":
    df_filtre = df_filtre[df_filtre["Département"] == filtre_dept]

if filtre_genre != "Tous":
    df_filtre = df_filtre[df_filtre["Genre"] == filtre_genre]

if recherche:
    df_filtre = df_filtre[
        df_filtre["Prénom"].str.contains(recherche, case=False, na=False) |
        df_filtre["Nom"].str.contains(recherche, case=False, na=False)
    ]

st.markdown(f"**{len(df_filtre)} patient(s) affiché(s)**")

# =========================================
# TABLEAU
# =========================================

st.dataframe(df_filtre, use_container_width=True)

st.markdown("---")

# =========================================
# SUPPRIMER UN PATIENT
# =========================================

st.subheader("Supprimer un patient")

id_delete = st.number_input("ID du patient à supprimer", min_value=1, step=1)

if st.button("Supprimer"):
    delete_patient(id_delete)
    st.success(f"Patient ID {id_delete} supprimé avec succès")
    st.rerun()