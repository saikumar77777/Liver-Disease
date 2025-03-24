import streamlit as st

# Navigation function
def navigate_to_page(page_name):
    st.session_state["current_page"] = page_name
    st.experimental_rerun()

def home_page():
    # Apply background styling
    st.markdown(
        """
        <style>
        .main {
            background-image: url("https://img.freepik.com/premium-photo/soft-pastel-texture-background-beautiful-texture-background-bg-paint-texture_1020697-465337.jpg");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Top Section: Title and Signup Button in Two Columns
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <h1 style='text-align: left; font-size: 60px;'>Predict Liver Disease</h1>
        <p style='text-align: left; font-size: 20px;'>Get Personalised health Insights.</p>
        """, unsafe_allow_html=True)
        if st.button("Get Started", type="primary"):
            navigate_to_page("login")

    with col2:
        st.image("https://cdni.iconscout.com/illustration/premium/thumb/doctor-showing-liver-checkup-report-illustration-download-in-svg-png-gif-file-formats--medical-record-healthcare-pack-illustrations-10127602.png", width=300)

    # Middle Section: Features in Three Columns
    st.markdown("---")
    st.markdown(
        """
        <style>
        .feature-box {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            width: 100%;
        }
        .feature-box img {
            display: block;
            margin: 0 auto;
        }
        .feature-box h3, .feature-box p {
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Create three columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-box">
                <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQV6O-dlnGzRd2J16wFTjg82FZk1JAWeXrkpw&s" width="100">
                <h3 style='text-align: center; color: #0694d1;'>Healthy liver, healthy life</h3>
                <p>Get personalized health insights and improve your liver health.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="feature-box">
                <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRVUxZqsG2UseFv91O0rqlOKNO6obKkBZk5Og&s" width="100">
                <h3 style='text-align: center; color: #0694d1;'>Better Sleep</h3>
                <p>Imporve your sleep and wakr up refereshed with peroanlized insights and lifestyle changes.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="feature-box">
                <img src="https://t4.ftcdn.net/jpg/05/74/40/37/360_F_574403725_qdGsgxEYqL16NyElPiwNq1CgIgIKfMe4.jpg" width="120">
                <h3 style='text-align: center; color: #0694d1;'>Less Stress</h3>
                <p>Reduce stress and improve your mental health with personalized insights.</p>
            """,
            unsafe_allow_html=True
        )
    # Bottom Section: Image and Why Choose Us
    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.image("https://cdni.iconscout.com/illustration/premium/thumb/doctor-with-stethoscope-illustration-download-in-svg-png-gif-file-formats--physicians-therapists-general-practitioners-pack-people-illustrations-3741685.png?f=webp", width=400)

    with col2:
        st.markdown("""
        <h2 style='text-align: left; font-size: 40px; color: #0694d1;'>Why Choose HepaWise?</h2>
        <ul>
            <li style='font-size: 20px;'>Boost liver function with personalized tips.</li>  
            <li style='font-size: 20px;'>Track and improve your liver health easily.</li>  
            <li style='font-size: 20px;'>Reduce toxins and enhance liver wellness.</li>  
            <li style='font-size: 20px;'>Stay informed about liver-friendly habits.</li>  
        </ul>
        """, unsafe_allow_html=True)
