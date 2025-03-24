import streamlit as st
from streamlit_option_menu import option_menu
from database import fetch_user
import joblib
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import google.generativeai as genai
import smtplib
import geocoder
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from database import fetch_user
import pdfplumber
import re
liver_recommendations = {
    "ast_sgot": {
        "normal": "Your AST (SGOT) levels are within the normal range. Continue maintaining a healthy lifestyle with a balanced diet.",
        "abnormal": "Elevated AST (SGOT) levels may indicate liver damage. Avoid alcohol, processed foods, and excessive fats. Include more antioxidant-rich foods like leafy greens and berries."
    },
    "alt_sgot": {
        "normal": "Your ALT (SGPT) levels are normal. Keep following a nutritious diet and stay active.",
        "abnormal": "High ALT (SGPT) levels can be a sign of liver inflammation. Reduce sugar intake, exercise regularly, and include liver-friendly foods like garlic, turmeric, and green tea."
    },
    "ast_alt_ratio": {
        "normal": "Your AST-ALT ratio is within a healthy range. Keep following good dietary habits and staying hydrated.",
        "abnormal": "A high AST-ALT ratio may indicate chronic liver disease. Prioritize liver detox foods such as beetroot, walnuts, and avocados while avoiding excess sodium and saturated fats."
    },
    "ggtp": {
        "normal": "Your GGTP levels are normal. Ensure you stay hydrated and maintain a liver-friendly diet.",
        "abnormal": "Elevated GGTP levels can be linked to liver dysfunction or alcohol-related issues. Avoid alcohol completely, drink more water, and consume fiber-rich foods like whole grains and legumes."
    },
    "alp": {
        "normal": "Your ALP levels are normal. Keep following a balanced diet and regular exercise routine.",
        "abnormal": "High ALP levels can indicate bile duct issues. Avoid fried foods, increase your intake of vitamin D-rich foods like eggs and fish, and engage in moderate exercise."
    },
    "bilirubin_total": {
        "normal": "Your total bilirubin levels are within normal limits. Continue maintaining a healthy lifestyle.",
        "abnormal": "Elevated bilirubin may suggest jaundice or liver stress. Stay hydrated, consume citrus fruits, and eat easily digestible foods like soups and boiled vegetables."
    },
    "bilirubin_direct": {
        "normal": "Your direct bilirubin levels are normal. Keep up your good health habits.",
        "abnormal": "High direct bilirubin may indicate bile obstruction. Reduce dairy intake, increase fiber consumption, and include probiotic foods like yogurt in your diet."
    },
    "bilirubin_indirect": {
        "normal": "Your indirect bilirubin levels are within a healthy range. Keep taking care of your liver.",
        "abnormal": "High indirect bilirubin may be due to liver dysfunction. Increase your intake of iron-rich foods like spinach and legumes while reducing fatty foods."
    },
    "total_protein": {
        "normal": "Your total protein levels are balanced. Ensure you have sufficient protein intake daily.",
        "abnormal": "Low protein levels may indicate poor liver function. Increase lean proteins like fish, eggs, and plant-based proteins while avoiding red meat."
    },
    "albumin": {
        "normal": "Your albumin levels are good. Keep following a nutritious diet and stay hydrated.",
        "abnormal": "Low albumin may be linked to chronic liver conditions. Increase protein intake, stay hydrated, and avoid processed foods."
    }
}
def generate_liver_recommendations(user_inputs):
    recommendations = []

    # Check each input parameter and append relevant recommendations
    for key, value in user_inputs.items():
        if value == "normal":
            recommendations.append(liver_recommendations[key]["normal"])
        else:
            recommendations.append(liver_recommendations[key]["abnormal"])

    return " ".join(recommendations)  # Combine all recommendations into a single paragraph
def classify_liver_parameters(ast_sgot, alt_sgot, ast_alt_ratio, ggtp, alp, bilirubin_total, 
                               bilirubin_direct, bilirubin_indirect, total_protein, albumin):
    user_inputs = {
        "ast_sgot": "normal" if 10 <= ast_sgot <= 40 else "abnormal",
        "alt_sgot": "normal" if 7 <= alt_sgot <= 56 else "abnormal",
        "ast_alt_ratio": "normal" if 0.8 <= ast_alt_ratio <= 1.2 else "abnormal",
        "ggtp": "normal" if 8 <= ggtp <= 61 else "abnormal",
        "alp": "normal" if 44 <= alp <= 147 else "abnormal",
        "bilirubin_total": "normal" if 0.1 <= bilirubin_total <= 1.2 else "abnormal",
        "bilirubin_direct": "normal" if 0.0 <= bilirubin_direct <= 0.3 else "abnormal",
        "bilirubin_indirect": "normal" if 0.1 <= bilirubin_indirect <= 1.0 else "abnormal",
        "total_protein": "normal" if 6.0 <= total_protein <= 8.3 else "abnormal",
        "albumin": "normal" if 3.5 <= albumin <= 5.0 else "abnormal"
    }
    
    return user_inputs
def disease_info_box(disease_name):
    return f"""
        <div style="
            background-color: rgba(233, 247, 99, 0.8);
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            font-size: 50px;
            font-weight: bold;
            color: red;
            margin-bottom:20px;">
            {disease_name}
        </div>
    """
def prevntions(disease_name):
    return f"""
        <div style="
            background-image:url(https://img.freepik.com/premium-photo/healthy-lifestyle-food-sport-concept-athlete-s-equipment-fresh-fruit-white-background_61573-3385.jpg);
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-color: rgba(255, 255, 255, 0.8);
            background-blend-mode: overlay;
            padding: 10px;
            border-radius: 10px;
            text-align: justify;
            font-size: 15px;
            color: black;">
            {disease_name}
        </div>
    """
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

def clean_number(value):
    if value:
        value = re.sub(r'\s+', '', value)  # Remove spaces
        value = re.sub(r'(\d+\.\d+)(\d+\.\d+)', r'\1, \2', value)  # Split concatenated decimals
    return value
def navigate_to_page(page_name):
    st.session_state["current_page"] = page_name
    st.experimental_rerun()

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"  # Extract text from each page
    return text

def user_home_page():
    user = fetch_user(st.session_state["current_user"])
    with st.sidebar:
        select = option_menu(
            f"Welcome, {user[1]}!",
            ["User Profile",'Disease Detection','Report Identification','Nearby Hospitals', "Feedback","ChatBot","Logout"],
            icons=['person-vcard-fill','cloud-upload','hospital','journals', 'chat-left-text-fill','box-arrow-right'], 
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
        )

    if select == 'User Profile':
        st.markdown(
        """
        <style>
        /* Apply background image to the main content area */
        .main {
            background-image: url('https://media.istockphoto.com/id/958522248/photo/the-concept-of-a-healthy-liver.jpg?s=612x612&w=0&k=20&c=WVarRCQ7LXNTGAWT0ItAsYD8oCjFoCIwHKRbsuJLP98=');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        </style>
        """,
        unsafe_allow_html=True
        )
        # Extracting user data from session state after successful login
        if user:
            # Assuming 'user' is a tuple (id, name, email, password, regd_no, year_of_study, branch, student_type, student_image)
            name, age, gender = user[1], user[3], user[4]
            student_image = user[6]  
            if isinstance(student_image, bytes):
                # Encode the binary image to base64
                image_data = base64.b64encode(student_image).decode()
                image_link = f"data:image/png;base64,{image_data}"
            elif isinstance(student_image, str) and student_image:  # In case it's a file path or URL
                try:
                    # Open the image as binary if it's a valid file path
                    with open(student_image, "rb") as img_file:
                        image_data = base64.b64encode(img_file.read()).decode()
                        image_link = f"data:image/png;base64,{image_data}"
                except FileNotFoundError:
                    # Default image in case file is not found
                    image_link = "https://cdn-icons-png.flaticon.com/512/4042/4042356.png"
            # CSS Styling for vertical container
            profile_css = """
            <style>
                .profile-container {
                    background-color: #a3ebff;
                    padding: 50px;
                    border-radius: 20px;
                    box-shadow: 10px 8px 12px rgba(0, 0, 0, 0.15);
                    max-width: 300px;
                    border: 2px solid black;
                    margin-left: 100%;
                    margin: auto;
                    font-family: Arial, sans-serif;
                    text-align: center;
                }
                .profile-header {
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 15px;
                    color: #333;
                }
                .profile-item {
                    font-size: 18px;
                    margin-bottom: 10px;
                    color: #555;
                }
                .profile-image img {
                    border-radius: 50%;
                    max-width: 200px;
                    max-height: 200px;
                    margin-bottom: 20px;
                }
            </style>
            """

            # HTML Structure for vertical alignment
            profile_html = f"""
            <div class="profile-container">
                <div class="profile-image">
                    <img src="{image_link}" alt="User Image">
                </div>
                <div class="profile-details">
                    <div class="profile-header">User Report</div>
                    <div class="profile-item"><strong>Name:</strong> {name}</div>
                    <div class="profile-item"><strong>Age:</strong> {age}</div>
                    <div class="profile-item"><strong>Gender:</strong> {gender}</div>
                </div>
            </div>
            """

            # Display styled content
            st.markdown(profile_css + profile_html, unsafe_allow_html=True)
    elif select == 'Nearby Hospitals':  
        st.markdown(
        """
        <style>
        /* Apply background image to the main content area */
        .main {
            background-image: url('https://img.freepik.com/premium-photo/abstract-blur-hospital-interior-corridor-background-with-defocused-effect_441990-15555.jpg?semt=ais_hybrid');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        </style>
        """,
        unsafe_allow_html=True
        )
        data = pd.read_csv('doctors.csv', encoding='utf-8', on_bad_lines='skip')
        # Predefined locations
        locations = [
            "Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool",
            "Rajahmundry", "Kakinada", "Tirupati", "Anantapur", "Kadapa",
            "Eluru", "Chittoor", "Machilipatnam", "Srikakulam", "Ongole",
            "Tenali", "Hindupur", "Proddatur", "Madanapalle"
        ]

        # UI: Title
        st.markdown('<h1 style="text-align: center; color: #333;">🏥 Nearby Hospitals</h1>', unsafe_allow_html=True)

        g = geocoder.ip('me')  # Fetches location based on your IP
        user_location = g.city  # Extract city from location
        col1,col2,col3=st.columns([1,2,1])
        loc = [
            " ","Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool",
            "Rajahmundry", "Kakinada", "Tirupati", "Anantapur", "Kadapa",
            "Eluru", "Chittoor", "Machilipatnam", "Srikakulam", "Ongole",
            "Tenali", "Hindupur", "Proddatur", "Madanapalle"
        ]
        user_loc=col3.selectbox("Select Your Location",loc)
        if user_loc==" ":
            if user_location in locations:
                filtered_data = data[data['Region'] == user_location]

                # Custom CSS for styling the container and button
                st.markdown(
                    """
                    <style>
                    .hospital-container {
                        background-color: #c4c4c2;
                        padding: 25px;
                        border-radius: 20px;
                        border: 2px solid #333;
                        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                        text-align: center;
                        margin-bottom: 15px;
                    }
                    .hospital-name {
                        font-size: 18px;
                        font-weight: bold;
                        color: #333;
                    }
                    .map-button {
                        background-color: red;
                        color: white !important;
                        padding: 8px 12px;
                        text-decoration: none;
                        border-radius: 5px;
                        display: inline-block;
                        margin-top: 10px;
                        font-weight: bold;
                    }
                    .map-button:hover {
                        background-color: blue;
                        color: white !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                # Create columns layout (3 per row)
                cols = st.columns(3)

                # Iterate through hospitals and distribute them across columns
                for index, row in enumerate(filtered_data.iterrows()):
                    col = cols[index % 3]  # Distribute across 3 columns
                    with col:
                        st.markdown(
                            f"""
                            <div class="hospital-container">
                                <div class="hospital-name">{row[1]['Hospital Name']}</div>
                                <a href="{row[1]['Map Link']}" target="_blank" class="map-button">🚖 View on Map</a>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
            else:
                # Initialize Gemini API
                genai.configure(api_key="AIzaSyCEHqEUnURAuH54Tng8IjlWSR6LyzzEpCI")
                model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

                if user_location:
                    # Ask Gemini API to find the nearest location
                    prompt = f"From the given list of locations {locations}, find the nearest one to {user_location}. If none, respond with 'Sorry, unable to find'."
                    response = model.generate_content([prompt]).text.strip()
                    match = re.search(r'\b(?:' + '|'.join(locations) + r')\b', response)
                    if match:
                        nearest_city = match.group(0)  # Extracted city name
                        filtered_data = data[data['Region'] == nearest_city]

                        # Custom CSS for styling the container and button
                        st.markdown(
                            """
                            <style>
                            .hospital-container {
                                background-color: #c4c4c2;
                                padding: 25px;
                                border-radius: 20px;
                                border: 2px solid #333;
                                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                                text-align: center;
                                margin-bottom: 15px;
                            }
                            .hospital-name {
                                font-size: 18px;
                                font-weight: bold;
                                color: #333;
                            }
                            .map-button {
                                background-color: red;
                                color: white !important;
                                padding: 8px 12px;
                                text-decoration: none;
                                border-radius: 5px;
                                display: inline-block;
                                margin-top: 10px;
                                font-weight: bold;
                            }
                            .map-button:hover {
                                background-color: blue;
                                color: white !important;
                            }
                            </style>
                            """,
                            unsafe_allow_html=True
                        )

                        # Create columns layout (3 per row)
                        cols = st.columns(3)

                        # Iterate through hospitals and distribute them across columns
                        for index, row in enumerate(filtered_data.iterrows()):
                            col = cols[index % 3]  # Distribute across 3 columns
                            with col:
                                st.markdown(
                                    f"""
                                    <div class="hospital-container">
                                        <div class="hospital-name">{row[1]['Hospital Name']}</div>
                                        <a href="{row[1]['Map Link']}" target="_blank" class="map-button">🚖 View on Map</a>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                
        else:
            filtered_data = data[data['Region'] == user_loc]
            # Custom CSS for styling the container and button
            st.markdown(
                """
                <style>
                .hospital-container {
                    background-color: #c4c4c2;
                    padding: 25px;
                    border-radius: 20px;
                    border: 2px solid #333;
                    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    margin-bottom: 15px;
                }
                .hospital-name {
                    font-size: 18px;
                    font-weight: bold;
                    color: #333;
                }
                .map-button {
                    background-color: red;
                    color: white !important;
                    padding: 8px 12px;
                    text-decoration: none;
                    border-radius: 5px;
                    display: inline-block;
                    margin-top: 10px;
                    font-weight: bold;
                }
                .map-button:hover {
                    background-color: blue;
                    color: white !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            # Create columns layout (3 per row)
            cols = st.columns(3)

            # Iterate through hospitals and distribute them across columns
            for index, row in enumerate(filtered_data.iterrows()):
                col = cols[index % 3]  # Distribute across 3 columns
                with col:
                    st.markdown(
                        f"""
                        <div class="hospital-container">
                            <div class="hospital-name">{row[1]['Hospital Name']}</div>
                            <a href="{row[1]['Map Link']}" target="_blank" class="map-button">🚖 View on Map</a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    elif select == 'Feedback':
        st.markdown(
        """
        <style>
        /* Apply background image to the main content area */
        .main {
            background-image: url("https://img.freepik.com/free-psd/3d-emoji-frame-isolated_23-2151171338.jpg?semt=ais_hybrid");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        </style>
        """,
        unsafe_allow_html=True
        )
        with st.form('About Us'):
            # Contact Us Form
            st.subheader(f"Hello {user[1]} Fill Feedback!! ✍️")

            # Create form fields
            name = user[1]
            email = user[2]
            phone = st.text_input("Phone Number")
            issue = st.text_area("Describe your Feedback!!")

            # Submit button
            if st.form_submit_button("Submit"):
                if issue and phone:
                    to_email=user[2]
                    subject = "Liver Disease Detection Feedback"
                    message = f"Hello {name},\n\nThank you for your feedback. We will get back to you soon.\n\nRegards,\nLiver Disease Detection Team"
                    #combine message and feedback
                    from_email = 'noreply.vvit.college@gmail.com'
                    from_password = 'wugwrszzbcxcujif'  
                    # Send the alert email
                    send_alert_email(to_email, subject, message, from_email, from_password)
                    message1 = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nFeedback: {issue}"
                    send_alert_email(from_email, "Feedback Received", message1, from_email, from_password)

                    st.success("Thank you for reaching out! We'll get back to you soon.")
                else:
                    st.error("Please fill in all fields before submitting.")
    elif select == 'Disease Detection':
        st.markdown('<h1 style="text-align: center; color: #333;">🔍 Liver Disease Detection</h1>', unsafe_allow_html=True)
        col1,col2=st.columns([1,1])
        model=joblib.load("liver_disease_model.pkl")
        age=user[3]
        sex = 0 if user[4]=='Male' else 1
        ast_sgot=col1.number_input("Enter AST (SGOT) Value",min_value=0.0,max_value=1000.0)
        alt_sgot=col2.number_input("Enter ALT (SGPT) Value",min_value=0.0,max_value=1000.0)
        col1,col2=st.columns([1,1])
        ast_alt_ratio=col1.number_input("Enter AST-ALT Ratio Value",min_value=0.0,max_value=1000.0)
        ggtp=col2.number_input("Enter GGTP Value",min_value=0.0,max_value=1000.0)
        col1,col2=st.columns([1,1])
        alp=col1.number_input("Enter ALP Value",min_value=0.0,max_value=1000.0)
        bilirubin_total=col2.number_input("Enter Bilirubin Total Value",min_value=0.0,max_value=1000.0)
        col1,col2=st.columns([1,1])
        bilirubin_direct=col1.number_input("Enter Bilirubin Direct Value",min_value=0.0,max_value=1000.0)
        bilirubin_indirect=col2.number_input("Enter Bilirubin Indirect Value",min_value=0.0,max_value=1000.0)
        col1,col2=st.columns([1,1])
        total_protein=col1.number_input("Enter Total Protein Value",min_value=0.0,max_value=1000.0)
        albumin=col2.number_input("Enter Albumin Value",min_value=0.0,max_value=1000.0)
        col1,col2,col3=st.columns([1,1,1])
        a_g_ratio=col2.number_input("Enter A-G Ratio Value",min_value=0.0,max_value=1000.0)

        col1,col2,col3=st.columns([2,2,1])
        if col2.button("Predict",type='primary'):
            user_input=[age,sex,ast_sgot,alt_sgot,ast_alt_ratio,ggtp,alp,bilirubin_total,bilirubin_direct,bilirubin_indirect,total_protein,albumin,a_g_ratio]
            pred=model.predict([user_input])[0]
            if pred==0:
                st.markdown(disease_info_box("You are Healthy and have no Liver Disease!!"),unsafe_allow_html=True)
            elif pred==1:
                st.markdown(disease_info_box("You have Fatty Liver Disease!!"),unsafe_allow_html=True)
            elif pred==2:
                st.markdown(disease_info_box("You have Hepatitis!!"),unsafe_allow_html=True)
            elif pred==3:
                st.markdown(disease_info_box("You have Cirrhosis!!"),unsafe_allow_html=True)
            elif pred==4:
                st.markdown(disease_info_box("You have Liver Cancer!!"),unsafe_allow_html=True)
            user_classification = classify_liver_parameters(ast_sgot, alt_sgot, ast_alt_ratio, ggtp, alp,
                                                    bilirubin_total, bilirubin_direct, bilirubin_indirect,
                                                    total_protein, albumin)
            recommendations_text = generate_liver_recommendations(user_classification)
            st.markdown(prevntions(recommendations_text),unsafe_allow_html=True)

    elif select == 'Report Identification':
        st.title("Liver Disease Detection")
        file=st.file_uploader("Upload Liver Function Test Report",type=['pdf'])
        try:
            if file is not None:
                text = extract_text_from_pdf(file)
                patterns = {
                    "Age": r'Age\s*:\s*(\d+)',
                    "Sex": r'Sex\s*:\s*(\w+)',
                    "AST (SGOT)": r'AST \(SGOT\)\s*([\d\s\.\,]+)',
                    "ALT (SGPT)": r'ALT \(SGPT\)\s*([\d\s\.\,]+)',
                    "AST:ALT Ratio": r'AST:ALT Ratio\s*([\d\s\.\,]+)',
                    "GGTP": r'GGTP\s*([\d\s\.\,]+)',
                    "ALP": r'Alkaline Phosphatase \(ALP\)\s*([\d\s\.\,]+)',
                    "Bilirubin Total": r'Bilirubin Total\s*([\d\s\.\,]+)',
                    "Bilirubin Direct": r'Bilirubin Direct\s*([\d\s\.\,]+)',
                    "Bilirubin Indirect": r'Bilirubin Indirect\s*([\d\s\.\,]+)',
                    "Total Protein": r'Total Protein\s*([\d\s\.\,]+)',
                    "Albumin": r'Albumin\s*([\d\s\.\,]+)',
                    "A:G Ratio": r'A : G Ratio\s*([\d\s\.\,]+)'
                }

                # Extract values using regex
                results = {}
                for key, pattern in patterns.items():
                    match = re.search(pattern, text)
                    if match:
                        results[key] = clean_number(match.group(1))  # Clean extracted number
                    else:
                        results[key] = None  # No match found
                #make a dataframe
                df = pd.DataFrame(results, index=[0])
                def clean_column(value):
                    if isinstance(value, str) and ',' in value:
                        value = value.split(',')[0]  # Extract first value
                    return round(float(value),2)  # Convert to integer

                # Apply cleaning function to relevant columns
                for col in df.columns:
                    if col not in ['Age', 'Sex']:
                        df[col] = df[col].apply(clean_column)
                #add clean data to results
                missing_values = df.isnull().sum().sum()
                if missing_values>10:
                    st.image('https://cdni.iconscout.com/illustration/premium/thumb/forget-password-illustration-download-in-svg-png-gif-file-formats--wrong-forgot-invalid-login-credentials-empty-state-pack-design-development-illustrations-4503308.png?f=webp',use_column_width=True)
                    st.markdown('<h1 style="text-align: center; color: red;">Kindly  Upload Correct Report</h1>', unsafe_allow_html=True)
                elif missing_values<=10 and missing_values>0:
                    #fill missing values WITH 0.0001
                    df.fillna(0,inplace=True)
                    st.markdown("### 📊 Liver Function Test Report")
                    st.write(df)
                    model=joblib.load("liver_disease_model.pkl")
                    age=df['Age'][0]
                    sex=df['Sex'][0] if type(df['Sex'][0])==int else 0
                    ast_sgot=df['AST (SGOT)'][0]
                    alt_sgot=df['ALT (SGPT)'][0]
                    ast_alt_ratio=df['AST:ALT Ratio'][0]
                    ggtp=df['GGTP'][0]
                    alp=df['ALP'][0]
                    bilirubin_total=df['Bilirubin Total'][0]
                    bilirubin_direct=df['Bilirubin Direct'][0]
                    bilirubin_indirect=df['Bilirubin Indirect'][0]
                    total_protein=df['Total Protein'][0]
                    albumin=df['Albumin'][0]
                    a_g_ratio=df['A:G Ratio'][0]
                    user_input=[age,sex,ast_sgot,alt_sgot,ast_alt_ratio,ggtp,alp,bilirubin_total,bilirubin_direct,bilirubin_indirect,total_protein,albumin,a_g_ratio]
                    pred=model.predict([user_input])[0]
                    if pred==0:
                        st.markdown(disease_info_box("You are Healthy and have no Liver Disease!!"),unsafe_allow_html=True)
                    elif pred==1:
                        st.markdown(disease_info_box("You have Fatty Liver Disease!!"),unsafe_allow_html=True)
                    elif pred==2:
                        st.markdown(disease_info_box("You have Hepatitis!!"),unsafe_allow_html=True)
                    elif pred==3:
                        st.markdown(disease_info_box("You have Cirrhosis!!"),unsafe_allow_html=True)
                    elif pred==4:
                        st.markdown(disease_info_box("You have Liver Cancer!!"),unsafe_allow_html=True)
                    if pred:
                        user_input = [
                            ast_sgot, alt_sgot, ast_alt_ratio, ggtp, alp, 
                            bilirubin_total, bilirubin_direct, bilirubin_indirect, 
                            total_protein, albumin, a_g_ratio
                        ]

                        healthy_values = {
                            "AST (SGOT)": (10 + 40) / 2, 
                            "ALT (SGPT)": (7 + 56) / 2, 
                            "AST:ALT Ratio": (0.7 + 1.5) / 2, 
                            "GGTP": (8 + 61) / 2, 
                            "ALP": (44 + 147) / 2, 
                            "Bilirubin Total": (0.1 + 1.2) / 2, 
                            "Bilirubin Direct": (0.1 + 0.4) / 2, 
                            "Bilirubin Indirect": (0.2 + 0.7) / 2, 
                            "Total Protein": (6 + 8) / 2, 
                            "Albumin": (3.5 + 5.5) / 2, 
                            "A:G Ratio": (1.0 + 2.2) / 2
                        }
                        healthy_means = list(healthy_values.values())
                        labels = list(healthy_values.keys())

                        # 📊 **Interactive Bar Chart**
                        fig_bar = go.Figure()

                        fig_bar.add_trace(go.Bar(
                            x=labels, y=healthy_means, name="Healthy Values",
                            marker=dict(color='green'), text=healthy_means, textposition="auto"
                        ))

                        fig_bar.add_trace(go.Bar(
                            x=labels, y=user_input, name="User Values",
                            marker=dict(color='red'), text=user_input, textposition="auto"
                        ))

                        fig_bar.update_layout(
                            title="Healthy vs. User-Provided Liver Function Values",
                            xaxis_title="Liver Function Parameters",
                            yaxis_title="Values",
                            barmode="group",
                            hovermode="x unified"
                        )

                        st.plotly_chart(fig_bar)  # Display bar chart in Streamlit
                        user_classification = classify_liver_parameters(ast_sgot, alt_sgot, ast_alt_ratio, ggtp, alp,
                                                    bilirubin_total, bilirubin_direct, bilirubin_indirect,
                                                    total_protein, albumin)
                        recommendations_text = generate_liver_recommendations(user_classification)
                        st.markdown(prevntions(recommendations_text),unsafe_allow_html=True)

                else:
                    st.markdown("### 📊 Liver Function Test Report")
                    def clean_column(value):
                        if isinstance(value, str) and ',' in value:
                            value = value.split(',')[0]  # Extract first value
                        return round(float(value),2)  # Convert to integer

                    # Apply cleaning function to relevant columns
                    for col in df.columns:
                        if col not in ['Age', 'Sex']:
                            df[col] = df[col].apply(clean_column)
                    st.write(df)
                    model=joblib.load("liver_disease_model.pkl")
                    age=df['Age'][0]
                    sex=0 if df['Sex'][0]=='Male' else 1
                    ast_sgot=df['AST (SGOT)'][0]
                    alt_sgot=df['ALT (SGPT)'][0]
                    ast_alt_ratio=df['AST:ALT Ratio'][0]
                    ggtp=df['GGTP'][0]
                    alp=df['ALP'][0]
                    bilirubin_total=df['Bilirubin Total'][0]
                    bilirubin_direct=df['Bilirubin Direct'][0]
                    bilirubin_indirect=df['Bilirubin Indirect'][0]
                    total_protein=df['Total Protein'][0]
                    albumin=df['Albumin'][0]
                    a_g_ratio=df['A:G Ratio'][0]
                    user_input=[age,sex,ast_sgot,alt_sgot,ast_alt_ratio,ggtp,alp,bilirubin_total,bilirubin_direct,bilirubin_indirect,total_protein,albumin,a_g_ratio]
                    pred=model.predict([user_input])[0]
                    condition_map = {0: "Healthy", 1: "Fatty Liver", 2: "Hepatitis", 3: "Cirrhosis", 4: "Liver Cancer"}
                    if pred==0:
                        st.markdown(disease_info_box("You are Healthy and have no Liver Disease!!"),unsafe_allow_html=True)
                    elif pred==1:
                        st.markdown(disease_info_box("You have Fatty Liver Disease!!"),unsafe_allow_html=True)
                    elif pred==2:
                        st.markdown(disease_info_box("You have Hepatitis!!"),unsafe_allow_html=True)
                    elif pred==3:
                        st.markdown(disease_info_box("You have Cirrhosis!!"),unsafe_allow_html=True)
                    elif pred==4:
                        st.markdown(disease_info_box("You have Liver Cancer!!"),unsafe_allow_html=True)
                    user_input = [
                        ast_sgot, alt_sgot, ast_alt_ratio, ggtp, alp, 
                        bilirubin_total, bilirubin_direct, bilirubin_indirect, 
                        total_protein, albumin, a_g_ratio
                    ]

                    healthy_values = {
                        "AST (SGOT)": (10 + 40) / 2, 
                        "ALT (SGPT)": (7 + 56) / 2, 
                        "AST:ALT Ratio": (0.7 + 1.5) / 2, 
                        "GGTP": (8 + 61) / 2, 
                        "ALP": (44 + 147) / 2, 
                        "Bilirubin Total": (0.1 + 1.2) / 2, 
                        "Bilirubin Direct": (0.1 + 0.4) / 2, 
                        "Bilirubin Indirect": (0.2 + 0.7) / 2, 
                        "Total Protein": (6 + 8) / 2, 
                        "Albumin": (3.5 + 5.5) / 2, 
                        "A:G Ratio": (1.0 + 2.2) / 2
                    }
                    healthy_means = list(healthy_values.values())
                    labels = list(healthy_values.keys())

                    # 📊 **Interactive Bar Chart**
                    fig_bar = go.Figure()

                    fig_bar.add_trace(go.Bar(
                        x=labels, y=healthy_means, name="Healthy Values",
                        marker=dict(color='green'), text=healthy_means, textposition="auto"
                    ))

                    fig_bar.add_trace(go.Bar(
                        x=labels, y=user_input, name="User Values",
                        marker=dict(color='red'), text=user_input, textposition="auto"
                    ))

                    fig_bar.update_layout(
                        title="Healthy vs. User-Provided Liver Function Values",
                        xaxis_title="Liver Function Parameters",
                        yaxis_title="Values",
                        barmode="group",
                        hovermode="x unified"
                    )

                    st.plotly_chart(fig_bar)  # Display bar chart in Streamlit
                    user_classification = classify_liver_parameters(ast_sgot, alt_sgot, ast_alt_ratio, ggtp, alp,
                                                bilirubin_total, bilirubin_direct, bilirubin_indirect,
                                                total_protein, albumin)
                    recommendations_text = generate_liver_recommendations(user_classification)
                    st.markdown(prevntions(recommendations_text),unsafe_allow_html=True)
            else:
                st.image('https://cdni.iconscout.com/illustration/premium/thumb/help-liver-illustration-download-in-svg-png-gif-file-formats--holding-a-signboard-sign-board-pack-healthcare-medical-illustrations-2252541.png',use_column_width=True)
        except Exception as e:
            col1,col2,col3=st.columns([1,2,1])
            col2.image('https://static.vecteezy.com/system/resources/previews/029/194/739/non_2x/color-icon-for-invalid-vector.jpg')
    elif select == 'ChatBot':
        # Styling
        st.markdown(
            """
            <style>
            .main {
                background-image: url('https://wallpapers.com/images/hd/plain-white-background-3qzwpiavktxg11pr.jpg');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

                # Configure API Key
        api_key = "AIzaSyCEHqEUnURAuH54Tng8IjlWSR6LyzzEpCI"
        genai.configure(api_key=api_key)

        # Initialize the model
        model1 = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

        st.title("Liver Disease ChatBot")
        st.markdown("Ask me anything about liver diseases...")

        # Initialize session state for chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User Input
        user_input = st.chat_input("Ask me anything about the liver...")

        if user_input:
            # Append user message to session and display it
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Handle general greetings separately
            greetings = ["hi", "hello", "hey", "gm", "good morning", "good evening", "good night"]
            if user_input.lower() in greetings:
                bot_response = "Hello! How can I assist you with liver-related queries? 😊"
            
            else:
                # Check if the input is related to the eye
                check_prompt = f"Is the following question related to the Liver? Answer only 'yes' or 'no'. Question: {user_input}"
                check_response = model1.generate_content([check_prompt]).text.strip().lower()

                if check_response == "yes":
                    # Generate response from Gemini API
                    bot_prompt = f"Answer the following question in detail: {user_input} in 1 paragraph."
                    response = model1.generate_content([bot_prompt])
                    bot_response = response.text
                else:
                    bot_response = "Please ask a relevant question about the Liver."

            # Append bot response to session and display it
            st.session_state.messages.append({"role": "bot", "content": bot_response})
            with st.chat_message("bot"):
                st.markdown(bot_response)
    elif select == 'Logout':
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = None
        st.session_state.messages = []
        navigate_to_page("home")
            
