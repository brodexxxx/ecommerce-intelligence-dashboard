import streamlit as st

def login():
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # In real life, use a secure check!
        if username == "admin" and password == "yourpassword":
            st.session_state["logged_in"] = True
        else:
            st.error("Wrong username or password.")

if "logged_in" not in st.session_state:
    login()
else:
    st.write("Welcome!")
