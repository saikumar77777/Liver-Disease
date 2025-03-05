import streamlit as st
from database import authenticate_user,update_otp
import random
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
def send_alert_email(to_email, subject, message, from_email, from_password):
    # Set up the SMTP server
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    
    try:
        # Connect to the server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Alert email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

def navigate_to_page(page_name):
    st.session_state["current_page"] = page_name
    st.experimental_rerun()

def login_page():
    # Center the login form using Streamlit form layout
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
    #add space
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    with st.form(key="login_form"):
        # Title
        st.markdown(
            """
            <div style="text-align: center; color: red;">
                <h1 style="font-size: 50px; color:blue;">Login Here !!</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Email and Password inputs
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        # Submit button inside the form
        col1,col2,col3=st.columns([1,2,1])
        with col1:
            if st.form_submit_button("Verify",type='primary'):
                if authenticate_user(email, password):
                    st.success(f"Login successful. Welcome {email}!")
                    otp = random.randint(100000, 999999)
                    update_otp(email, otp)
                    to_email=email
                    subject = "OTP for Liver Disease Detection"
                    message = f"Hello,\n\nYour OTP for Liver Disease Detection is: {otp}\n\nRegards,\nLiver Disease Detection Team"
                    from_email = 'noreply.vvit.college@gmail.com'
                    from_password = 'wugwrszzbcxcujif'  
                    # Send the alert email
                    send_alert_email(to_email, subject, message, from_email, from_password)
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = email

                    navigate_to_page("otp")
                else:
                    st.error("Invalid email or password.")
        with col3:
            if st.form_submit_button("Create an account?",type='primary'):
                navigate_to_page("signup")