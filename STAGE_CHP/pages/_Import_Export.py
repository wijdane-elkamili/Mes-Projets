import streamlit as st
import pandas as pd
from database import add_patient, get_patients, delete_all_patients

if "user" not in st.session_state:
    st.warning("Veuillez vous connecter")
    st.stop()

st.title("Import / Export")

# =========================================
# IMPORT
# =========================================

st.subheader("Importer un fichier CSV")

file = st.file_uploader("Choisir un fichier CSV", type=["csv"])

if file:
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    st.success(f"Fichier chargé — {len(df)} lignes et {len(df.columns)} colonnes détectées")
    st.subheader("Aperçu du fichier")
    st.dataframe(df.head(5))

    st.markdown("---")
    st.subheader("Associer les colonnes de votre fichier")
    st.info("Associez les colonnes de votre fichier aux champs de l'application. Si une colonne n'existe pas, laissez 'Aucune'.")

    colonnes_disponibles = ["Aucune"] + df.columns.tolist()

    col1, col2 = st.columns(2)

    with col1:
        col_prenom = st.selectbox("Colonne Prénom", colonnes_disponibles,
            index=colonnes_disponibles.index(next((c for c in df.columns if c.lower() in ["prénom","prenom","first_name","firstname"]), "Aucune")))

        col_nom = st.selectbox("Colonne Nom", colonnes_disponibles,
            index=colonnes_disponibles.index(next((c for c in df.columns if c.lower() in ["nom","last_name","lastname"]), "Aucune")))

        col_age = st.selectbox("Colonne Age", colonnes_disponibles,
            index=colonnes_disponibles.index(next((c for c in df.columns if c.lower() in ["age","âge","age"]), "Aucune")))

        col_genre = st.selectbox("Colonne Genre", colonnes_disponibles,
            index=colonnes_disponibles.index(next((c for c in df.columns if c.lower() in ["genre","sexe","gender","sex"]), "Aucune")))

    with col2:
        col_dept = st.selectbox("Colonne Département", colonnes_disponibles,
            index=colonnes_disponibles.index(next((c for c in df.columns if c.lower() in ["département","department","service","provenance"]), "Aucune")))

        col_attente = st.selectbox("Colonne Temps Attente", colonnes_disponibles,
            index=colonnes_disponibles.index(next((c for c in df.columns if c.lower() in ["temps attente","waiting_time","attente","temps_attente"]), "Aucune")))

        col_priorite = st.selectbox("Colonne Priorité", colonnes_disponibles,
            index=colonnes_disponibles.index(next((c for c in df.columns if c.lower() in ["priorité","priority","triage","triage_niveau"]), "Aucune")))

    st.markdown("---")

    # Valeurs par défaut si colonne non associée
    default_prenom   = st.text_input("Prénom par défaut si non renseigné", "Inconnu")
    default_nom      = st.text_input("Nom par défaut si non renseigné", "Inconnu")
    default_age      = st.number_input("Age par défaut si non renseigné", value=0)
    default_genre    = st.selectbox("Genre par défaut", ["Non renseigné", "Homme", "Femme"])
    default_dept     = st.text_input("Département par défaut", "Urgences")
    default_attente  = st.number_input("Temps Attente par défaut (min)", value=0)
    default_priorite = st.selectbox("Priorité par défaut", ["Normal", "P1", "P2", "P3", "P4", "Urgent", "Critique"])

    if st.button("Confirmer l'import et enregistrer dans la base"):
        compteur = 0
        erreurs = 0

        for _, row in df.iterrows():
            try:
                add_patient(
                    first_name = str(row[col_prenom]) if col_prenom != "Aucune" else default_prenom,
                    last_name  = str(row[col_nom])    if col_nom    != "Aucune" else default_nom,
                    age        = int(float(row[col_age]))      if col_age     != "Aucune" and str(row[col_age]).replace('.','').isdigit()     else int(default_age),
                    gender     = str(row[col_genre])   if col_genre   != "Aucune" else default_genre,
                    department = str(row[col_dept])    if col_dept    != "Aucune" else default_dept,
                    waiting_time = int(float(row[col_attente])) if col_attente != "Aucune" and str(row[col_attente]).replace('.','').isdigit() else int(default_attente),
                    priority   = str(row[col_priorite]) if col_priorite != "Aucune" else default_priorite,
                )
                compteur += 1
            except Exception as e:
                erreurs += 1

        if compteur > 0:
            st.success(f"{compteur} patient(s) enregistré(s) avec succès")
        if erreurs > 0:
            st.warning(f"{erreurs} ligne(s) ignorée(s)")

st.markdown("---")

# =========================================
# EXPORT
# =========================================

st.subheader("Exporter les patients")

data = get_patients()

if data:
    df_export = pd.DataFrame(data, columns=[
        "ID", "Prénom", "Nom", "Age", "Genre", "Département", "Temps Attente", "Priorité"
    ])

    st.dataframe(df_export)
    st.metric("Total patients", len(df_export))

    csv = df_export.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Télécharger la liste des patients (CSV)",
        data=csv,
        file_name="patients_export.csv",
        mime="text/csv"
    )
else:
    st.info("Aucun patient dans la base de données")

st.markdown("---")

# =========================================
# SUPPRIMER TOUTES LES DONNÉES
# =========================================

st.subheader("Supprimer les données")

st.warning("Cette action supprime définitivement tous les patients de la base de données.")

if st.button("Supprimer toutes les données"):
    delete_all_patients()
    st.success("Toutes les données ont été supprimées. Vous pouvez importer un nouveau fichier.")
    st.rerun()