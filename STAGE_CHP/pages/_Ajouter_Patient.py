import streamlit as st
from database import add_patient, get_patients
import pandas as pd

if "user" not in st.session_state:
    st.warning("Veuillez vous connecter")
    st.stop()

st.title("Ajouter un patient")

# =========================================
# FORMULAIRE
# =========================================

st.subheader("Informations du patient")

col1, col2 = st.columns(2)

with col1:
    first_name = st.text_input("Prénom", placeholder="Ex: Wijdane")
    last_name = st.text_input("Nom", placeholder="Ex: EL KAMILI")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    gender = st.selectbox("Genre", ["Homme", "Femme", "Non renseigné"])

with col2:
    department = st.selectbox("Département", [
        "Urgences", "Cardiologie", "Pédiatrie", "Traumatologie",
        "Neurologie", "Gynécologie", "Orthopédie", "Autre"
    ])
    waiting_time = st.number_input("Temps d'attente (min)", min_value=0, max_value=600, step=5)
    priority = st.selectbox("Priorité", ["P1", "P2", "P3", "P4", "Critique", "Urgent", "Normal"])

st.markdown("---")

# =========================================
# VALIDATION ET AJOUT
# =========================================

if st.button("Ajouter le patient"):
    if not first_name.strip():
        st.error("Le prénom est obligatoire.")
    elif not last_name.strip():
        st.error("Le nom est obligatoire.")
    elif age == 0:
        st.warning("Vérifiez l'âge du patient.")
    else:
        add_patient(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            age=int(age),
            gender=gender,
            department=department,
            waiting_time=int(waiting_time),
            priority=priority
        )
        st.success(f"Patient {first_name} {last_name} ajouté avec succès !")

st.markdown("---")

# =========================================
# DERNIERS PATIENTS AJOUTÉS
# =========================================

st.subheader("Derniers patients ajoutés")

data = get_patients()

if data:
    df = pd.DataFrame(data, columns=[
        "ID", "Prénom", "Nom", "Age", "Genre", "Département", "Temps Attente", "Priorité"
    ])
    st.dataframe(df.tail(5), use_container_width=True)
    st.caption(f"Total : {len(df)} patient(s) dans la base")
else:
    st.info("Aucun patient dans la base de données.")