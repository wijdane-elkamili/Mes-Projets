import streamlit as st

# utilisateurs simples
users = {
    "admin": {"password": "1234", "role": "Admin"},
    "medecin": {"password": "1111", "role": "Médecin"}
}

def login():
    st.sidebar.title("🔐 Connexion")

    username = st.sidebar.text_input("Utilisateur")
    password = st.sidebar.text_input("Mot de passe", type="password")

    if st.sidebar.button("Se connecter"):
        if username in users and users[username]["password"] == password:
            st.session_state["user"] = username
            st.session_state["role"] = users[username]["role"]
            st.success("Connexion réussie")
        else:
            st.error("Identifiants incorrects")

def logout():
    if st.sidebar.button("Déconnexion"):
        st.session_state.clear()

def is_logged_in():
    return "user" in st.session_state