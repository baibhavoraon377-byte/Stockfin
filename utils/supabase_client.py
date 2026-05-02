import streamlit as st
from supabase import create_client, Client
import os

def get_supabase_client() -> Client:
    """
    Returns a fresh Supabase client instance for the current session.
    It automatically applies the authenticated user's session if they are logged in.
    """
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    client = create_client(url, key)
    
    if "access_token" in st.session_state and "refresh_token" in st.session_state:
        try:
            client.auth.set_session(
                st.session_state["access_token"], 
                st.session_state["refresh_token"]
            )
        except Exception:
            pass # Session might have expired
            
    return client

def is_authenticated() -> bool:
    return "user" in st.session_state and st.session_state["user"] is not None

def require_auth():
    """
    Shows a login/signup form if the user is not authenticated.
    Must be called at the top of pages that require authentication.
    """
    if is_authenticated():
        return True

    st.markdown("""
    <div style="text-align:center;padding:2rem">
        <h2 style="font-family:'Syne',sans-serif;color:#f0f2f8">Authentication Required</h2>
        <p style="color:#8892a4">Please login or sign up to access your personalized portfolio and watchlist.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    client = get_supabase_client()

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Log In", use_container_width=True):
                try:
                    response = client.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state["user"] = response.user
                    st.session_state["access_token"] = response.session.access_token
                    st.session_state["refresh_token"] = response.session.refresh_token
                    st.success("Logged in successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")

    with tab2:
        with st.form("signup_form"):
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign Up", use_container_width=True):
                try:
                    response = client.auth.sign_up({"email": new_email, "password": new_password})
                    st.success("Account created! You can now log in (if email confirmation is required, check your inbox).")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")

    return False

def logout():
    client = get_supabase_client()
    try:
        client.auth.sign_out()
    except:
        pass
    for key in ["user", "access_token", "refresh_token"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
