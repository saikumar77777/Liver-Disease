import streamlit as st
from streamlit_option_menu import option_menu
from database import fetch_user
import joblib
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from database import fetch_user
import pdfplumber
import re
def disease_info_box(disease_name):
    return f"""
        <div style="
            background-color: rgba(233, 247, 99, 0.8);
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            font-size: 50px;
            font-weight: bold;
            color: red;">
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
        # Load data
        data = pd.read_csv('doctors.csv', encoding='utf-8', on_bad_lines='skip')
        # UI: Select Region
        st.markdown('<h1 style="text-align: center; color: #333;">🏥 Nearby Hospitals</h1>', unsafe_allow_html=True)
        col1,col2,col3 = st.columns([1,4,1])
        selected_region = col2.selectbox('🌍 Select Region', data['Region'].unique())

        # Filter Data based on Selection
        filtered_data = data[data['Region'] == selected_region]

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

                        # 🕵️‍♂️ **Interactive Radar Chart (Spider Chart)**
                        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
                        healthy_means.append(healthy_means[0])  # Close radar chart loop
                        user_input.append(user_input[0])
                        angles.append(angles[0])

                        fig_radar = go.Figure()

                        fig_radar.add_trace(go.Scatterpolar(
                            r=healthy_means, theta=labels + [labels[0]], fill="toself",
                            name="Healthy Values", line=dict(color="green")
                        ))

                        fig_radar.add_trace(go.Scatterpolar(
                            r=user_input, theta=labels + [labels[0]], fill="toself",
                            name="User Values", line=dict(color="red")
                        ))

                        fig_radar.update_layout(
                            title="Radar Chart: Healthy vs. User Values",
                            polar=dict(radialaxis=dict(visible=True)),
                            hovermode="closest"
                        )

                        st.plotly_chart(fig_radar)  # Display radar chart in Streamlit

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
            else:
                st.image('https://cdni.iconscout.com/illustration/premium/thumb/help-liver-illustration-download-in-svg-png-gif-file-formats--holding-a-signboard-sign-board-pack-healthcare-medical-illustrations-2252541.png',use_column_width=True)
        except Exception as e:
            col1,col2,col3=st.columns([1,2,1])
            col2.image('https://static.vecteezy.com/system/resources/previews/029/194/739/non_2x/color-icon-for-invalid-vector.jpg')
            st.write(e)
    
    elif select == 'ChatBot':
        st.title("🤖 ChatBot")

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

        # Initialize session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "step" not in st.session_state:
            st.session_state.step = None
        if "input_data" not in st.session_state:
            st.session_state.input_data = {}
        if "close_session" not in st.session_state:
            st.session_state.close_session = False
        if "current_field" not in st.session_state:
            st.session_state.current_field = None

        # Greeting the user
        def greeting():
            hour = datetime.now().hour
            #show  4 greetings based on time
            if 6 <= hour < 12:
                return f"Good Morning!+{user[1]}"
            elif 12 <= hour < 18:
                return f"Good Afternoon! {user[1]}"
            elif 18 <= hour < 21:
                return f"Good Evening! {user[1]}"
            else:
                return f"Hello! {user[1]}"

        # Display previous messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Add initial bot greeting if no messages
        if not st.session_state.messages:
            greeting_message = f"Hello! {greeting()}"
            st.session_state.messages.append({"role": "bot", "content": greeting_message})
            with st.chat_message("bot"):
                st.markdown(greeting_message)

        # Process user input
        if user_input := st.chat_input("Your message here..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Main menu
            if st.session_state.step is None:
                if user_input.strip().lower() in ["hi", "hello", "hey","hii","hlo"]:
                    bot_response = "Hello! How can I help you today?"
                elif 'help' in user_input or 'Help' in user_input:
                    bot_response = "I can help you with the following, Liver Disease Information, Prevention, Symptoms, Treatment, Nearby Hospitals"
                elif 'Liver Disease' in user_input or 'liver disease' in user_input or 'Liver' in user_input or 'liver' in user_input:
                    if 'information' in user_input or 'Information' in user_input:
                        bot_response = "Liver disease can be inherited (genetic) or caused by a variety of factors that damage the liver, such as viruses and alcohol use. Obesity is also associated with liver damage. Over time, damage to the liver results in scarring (cirrhosis), which can lead to liver failure, a life-threatening condition."
                    elif 'Prevention' in user_input or 'prevention' in user_input:
                        bot_response = "Liver disease can be prevented by avoiding excessive alcohol consumption, eating a healthy diet, maintaining a healthy weight, avoiding risky behavior, and getting vaccinated against hepatitis."
                    elif 'Symptoms' in user_input or 'symptoms' in user_input:
                        bot_response = "Symptoms of liver disease can include jaundice (yellowing of the skin and eyes), dark urine, abdominal pain and swelling, itchy skin, chronic fatigue, nausea or vomiting, loss of appetite, and swelling in the legs and ankles."
                    elif 'Treatment' in user_input or 'treatment' in user_input:
                        bot_response = "Treatment for liver disease depends on the underlying cause and may include lifestyle changes, medications, or surgery. In some cases, a liver transplant may be necessary."
                    elif 'cirrhosis' in user_input or 'Cirrhosis' in user_input:
                        bot_response = "Cirrhosis is a late stage of scarring (fibrosis) of the liver caused by many forms of liver diseases and conditions, such as hepatitis and chronic alcoholism."
                    elif 'Fatty Liver' in user_input or 'fatty liver' in user_input:
                        bot_response = "Fatty liver disease is a condition in which fat builds up in your liver. There are two main types: Nonalcoholic fatty liver disease (NAFLD) and Alcoholic fatty liver disease (AFLD)."
                    elif 'Hepatitis' in user_input or 'hepatitis' in user_input:
                        bot_response = "Hepatitis is an inflammation of the liver. The condition can be self-limiting or can progress to fibrosis (scarring), cirrhosis, or liver cancer."
                    elif 'cancer' in user_input or 'Cancer' in user_input:
                        bot_response = "Liver cancer is a type of cancer that starts in the liver. Some cancers develop outside the liver and spread to the area. However, only cancers that start in the liver are described as liver cancer."
                    else:
                        bot_response = "I can provide information on Liver Disease. What would you like to know?"
                elif 'Nearby Hospitals' in user_input or 'nearby hospitals' in user_input or 'Hospitals' in user_input or 'hospitals' in user_input:
                    bot_response = "Go to Nearby Hospitals Section and select your region to find the nearest hospitals."
                elif 'cirrhosis' in user_input or 'Cirrhosis' in user_input:
                    if 'information' in user_input or 'Information' in user_input:
                        bot_response = "Cirrhosis is a late stage of scarring (fibrosis) of the liver caused by many forms of liver diseases and conditions, such as hepatitis and chronic alcoholism."
                    elif 'Prevention' in user_input or 'prevention' in user_input:
                        bot_response = "Cirrhosis can be prevented by avoiding excessive alcohol consumption, maintaining a healthy weight, eating a healthy diet, and avoiding risky behavior."
                    elif 'Symptoms' in user_input or 'symptoms' in user_input:
                        bot_response = "Symptoms of cirrhosis can include fatigue, weakness, loss of appetite, nausea, weight loss, itching, easy bruising, and jaundice."
                    elif 'Treatment' in user_input or 'treatment' in user_input:
                        bot_response = "Treatment for cirrhosis may involve lifestyle changes, medications, or surgery. In some cases, a liver transplant may be necessary."
                    elif 'Diet' in user_input or 'diet' in user_input:
                        bot_response = "A healthy diet for cirrhosis includes plenty of fruits, vegetables, whole grains, and lean protein. Limiting salt, sugar, and unhealthy fats is also important."
                    else:
                        bot_response = "I can provide information on Cirrhosis. What would you like to know?"

                elif 'Fatty Liver' in user_input or 'fatty liver' in user_input:
                    if 'information' in user_input or 'Information' in user_input:
                        bot_response = "Fatty liver disease is a condition in which fat builds up in your liver. There are two main types: Nonalcoholic fatty liver disease (NAFLD) and Alcoholic fatty liver disease (AFLD)."
                    elif 'Prevention' in user_input or 'prevention' in user_input:
                        bot_response = "Fatty liver disease can be prevented by maintaining a healthy weight, eating a balanced diet, exercising regularly, and avoiding excessive alcohol consumption."
                    elif 'Symptoms' in user_input or 'symptoms' in user_input:
                        bot_response = "Symptoms of fatty liver disease can include fatigue, weakness, weight loss, abdominal pain, and swelling in the abdomen."
                    elif 'Treatment' in user_input or 'treatment' in user_input:
                        bot_response = "Treatment for fatty liver disease may involve lifestyle changes, medications, or surgery. In some cases, weight loss and exercise can help improve the condition."
                    elif 'Diet' in user_input or 'diet' in user_input:
                        bot_response = "A healthy diet for fatty liver disease includes plenty of fruits, vegetables, whole grains, and lean protein. Limiting sugar, salt, and unhealthy fats is also important."
                    else:
                        bot_response = "I can provide information on Fatty Liver Disease. What would you like to know?"
                elif 'Hepatitis' in user_input or 'hepatitis' in user_input:
                    if 'information' in user_input or 'Information' in user_input:
                        bot_response = "Hepatitis is an inflammation of the liver. The condition can be self-limiting or can progress to fibrosis (scarring), cirrhosis, or liver cancer."
                    elif 'Prevention' in user_input or 'prevention' in user_input:
                        bot_response = "Hepatitis can be prevented by getting vaccinated, practicing good hygiene, avoiding risky behavior, and not sharing needles or personal items."
                    elif 'Symptoms' in user_input or 'symptoms' in user_input:
                        bot_response = "Symptoms of hepatitis can include fatigue, fever, nausea, vomiting, abdominal pain, dark urine, and jaundice."
                    elif 'Treatment' in user_input or 'treatment' in user_input:
                        bot_response = "Treatment for hepatitis may involve medications, lifestyle changes, or surgery. In some cases, antiviral drugs can help manage the condition."
                    elif 'Types' in user_input or 'types' in user_input:
                        bot_response = "There are several types of hepatitis, including hepatitis A, B, C, D, and E. Each type is caused by a different virus and has different symptoms and treatments."
                    else:
                        bot_response = "I can provide information on Hepatitis. What would you like to know?"
                elif 'cancer' in user_input or 'Cancer' in user_input:
                    if 'information' in user_input or 'Information' in user_input:
                        bot_response = "Liver cancer is a type of cancer that starts in the liver. Some cancers develop outside the liver and spread to the area. However, only cancers that start in the liver are described as liver cancer."
                    elif 'Prevention' in user_input or 'prevention' in user_input:
                        bot_response = "Liver cancer can be prevented by avoiding excessive alcohol consumption, maintaining a healthy weight, eating a balanced diet, and getting vaccinated against hepatitis."
                    elif 'Symptoms' in user_input or 'symptoms' in user_input:
                        bot_response = "Symptoms of liver cancer can include weight loss, loss of appetite, nausea, vomiting, abdominal pain, and jaundice."
                    elif 'Treatment' in user_input or 'treatment' in user_input:
                        bot_response = "Treatment for liver cancer may involve surgery, chemotherapy, radiation therapy, or targeted therapy. In some cases, a liver transplant may be necessary."
                    elif 'Types' in user_input or 'types' in user_input:
                        bot_response = "There are several types of liver cancer, including hepatocellular carcinoma, cholangiocarcinoma, and angiosarcoma. Each type has different symptoms and treatments."
                    else:
                        bot_response = "I can provide information on Liver Cancer. What would you like to know?"
                elif 'Diet' in user_input or 'diet' in user_input:
                        bot_response = "A healthy diet for liver disease includes plenty of fruits, vegetables, whole grains, and lean protein. Limiting salt, sugar, and unhealthy fats is also important."
                elif 'Symptoms' in user_input or 'symptoms' in user_input:
                        bot_response = "Symptoms of liver disease can include jaundice (yellowing of the skin and eyes), dark urine, abdominal pain and swelling, itchy skin, chronic fatigue, nausea or vomiting, loss of appetite, and swelling in the legs and ankles."
                elif 'Treatment' in user_input or 'treatment' in user_input:
                        bot_response = "Treatment for liver disease depends on the underlying cause and may include lifestyle changes, medications, or surgery. In some cases, a liver transplant may be necessary."
                elif 'Prevention' in user_input or 'prevention' in user_input:
                        bot_response = "Liver disease can be prevented by avoiding excessive alcohol consumption, eating a healthy diet, maintaining a healthy weight, avoiding risky behavior, and getting vaccinated against hepatitis."
                elif 'Alcohol' in user_input or 'alcohol' in user_input:
                        bot_response = "Excessive alcohol consumption is a major risk factor for liver disease. Limiting alcohol intake can help reduce your risk of developing liver problems."
                elif 'Vaccination' in user_input or 'vaccination' in user_input:
                        bot_response = "Vaccination against hepatitis A and B can help prevent liver disease. Talk to your healthcare provider about getting vaccinated."
                elif 'Risk Factors' in user_input or 'risk factors' in user_input:
                        bot_response = "Risk factors for liver disease include obesity, diabetes, high blood pressure, high cholesterol, and a family history of liver problems."
                elif 'Healthy Lifestyle' in user_input or 'healthy lifestyle' in user_input:
                        bot_response = "Maintaining a healthy lifestyle can help prevent liver disease. This includes eating a balanced diet, exercising regularly, getting enough sleep, and avoiding harmful substances."
                elif 'Albumin' in user_input or 'albumin' in user_input:
                        bot_response = "Albumin is a protein made by the liver. Low levels of albumin in the blood can indicate liver disease or other health problems."
                elif 'Globulin' in user_input or 'globulin' in user_input:
                        bot_response = "Globulin is a group of proteins made by the liver. High or low levels of globulin in the blood can indicate liver disease, kidney disease, or other health problems."
                elif 'Bilirubin' in user_input or 'bilirubin' in user_input:
                        bot_response = "Bilirubin is a yellowish substance found in bile. High levels of bilirubin in the blood can indicate liver disease, anemia, or other health problems."
                elif 'Alkaline Phosphatase' in user_input or 'alkaline phosphatase' in user_input:
                        bot_response = "Alkaline phosphatase is an enzyme found in the liver, bones, and other tissues. High levels of alkaline phosphatase in the blood can indicate liver disease, bone disease, or other health problems."
                elif 'Alamine Aminotransferase' in user_input or 'alamine aminotransferase' in user_input:
                        bot_response = "Alamine aminotransferase (ALT) is an enzyme found in the liver. High levels of ALT in the blood can indicate liver disease, hepatitis, or other health problems."
                elif 'Aspartate Aminotransferase' in user_input or 'aspartate aminotransferase' in user_input:
                        bot_response = "Aspartate aminotransferase (AST) is an enzyme found in the liver, heart, and other tissues. High levels of AST in the blood can indicate liver disease, heart disease, or other health problems."
                elif 'Total Proteins' in user_input or 'total proteins' in user_input:
                        bot_response = "Total proteins are the total amount of protein in the blood. Low or high levels of total proteins can indicate liver disease, kidney disease, or other health problems."
                elif 'Albumin and Globulin Ratio' in user_input or 'albumin and globulin ratio' in user_input:
                        bot_response = "The albumin and globulin ratio is a measure of the balance between albumin and globulin in the blood. Abnormal levels of this ratio can indicate liver disease, kidney disease, or other health problems."
                elif 'Thank you' in user_input or 'thank you' in user_input or 'Thanks' in user_input or 'thanks' in user_input:
                        bot_response = "You're welcome! If you have any more questions, feel free to ask."
                elif 'bye' in user_input or 'Bye' in user_input or 'exit' in user_input or 'Exit' in user_input or 'quit' in user_input or 'Quit' in user_input:
                    bot_response = "Goodbye! Have a great day ahead. 👋"
                    st.session_state.close_session = True
                else:
                    bot_response = "I'm sorry, I didn't understand that.Try asking something else."
            else:
                bot_response = "I'm sorry, I didn't understand that. Please try again."

            # Append bot response
            st.session_state.messages.append({"role": "bot", "content": bot_response})
            with st.chat_message("bot"):
                if "I'm sorry" in bot_response:
                    st.error(bot_response)
                else:
                    st.success(bot_response)    
    elif select == 'Logout':
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = None
        st.session_state.messages = []
        navigate_to_page("home")
            