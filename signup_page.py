import streamlit as st
from database import add_user
import re
def navigate_to_page(page_name):
    st.session_state["current_page"] = page_name
    st.experimental_rerun()
def validate_mail(mail):
    valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', mail)
    return True
def is_valid_password(password):
    if (len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'\d', password) and
        re.search(r'[\W_]', password)):  # \W matches special characters, _ is included
        return True
    return False
def signup_page():
    st.markdown(
    """
    <style>
    /* Apply background image to the main content area */
    .main {
        background-image: url("https://www.ajhospital.in/storage/files/news/Blog/01.jpg");  
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-color: rgba(255, 255, 255, 0.6);
        background-blend-mode: overlay;

    }
    </style>
    """,
    unsafe_allow_html=True
    )
    st.markdown(
        """
        <div style="text-align: center; color: red;">
            <h1 style="font-size: 50px; color:blue;">Sign Up Here !!</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    with st.form(key="signup_form"):
        col1,col2=st.columns([1,1])
        name=col1.text_input("Enter Name",placeholder="Enter your name", key="signup_name")
        email = col2.text_input("Email", key="signup_email", placeholder="Enter your email address")
        col1,col2=st.columns([1,1])
        age=col1.slider("Age",value=25,min_value=1,max_value=100)
        gender=col2.selectbox("Gender", ["Male","Female","Other"])
        otp=None
        image=st.file_uploader("Upload your image",type=['jpg','png','jpeg'])
        col1,col2=st.columns([1,1])
        password = col1.text_input("Create a Password", type="password", key="signup_password",help="Password must be at least 8 characters long.",placeholder="Enter your password")
        retyped_password = col2.text_input("Retype Password", type="password", key="signup_retyped_password",help="Please retype the password.",placeholder="Retype your password")
        col1,col2,col3 = st.columns([1,1,1])
        with col1:
            if validate_mail(email)==None:
                st.error("Invalid email address. Please enter a valid email address.")
            elif password!=retyped_password:
                st.error("Passwords do not match.")
            elif len(password)<6 and len(password)!=0:
                st.error("Password must be at least 8 characters long.")
            elif is_valid_password(password)==False and len(password)!=0:
                st.error("kindly enter a strong password")
            if st.form_submit_button("Sign Up",type='primary') and validate_mail(email)!=None and len(password)>=6 and password==retyped_password and age and gender and name and image and is_valid_password(password):
                try:
                    add_user(name,email,age,gender,otp,image,password)
                    st.success("Account created successfully!!")
                    navigate_to_page("login")
                except Exception as e:
                    st.error(e)
        with col3:
            if st.form_submit_button("Already have an account?",type='primary'):
                navigate_to_page("login")