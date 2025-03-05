import streamlit as st

# Navigation function
def navigate_to_page(page_name):
    st.session_state["current_page"] = page_name
    st.experimental_rerun()
def home_page():
    st.markdown(
    """
    <style>
    /* Apply background image to the main content area */
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

    with st.form(key="home_page_form"):
        st.markdown(
            """
            <div style="text-align: center;">
                <h1>Liver Disease Predict System</h1>
            </div>
            """,
            unsafe_allow_html=True
        )
        #add image
        st.markdown(
            """
            <div style="text-align: center;">
                <img src="https://cdni.iconscout.com/illustration/premium/thumb/female-doctor-checking-lung-report-illustration-download-in-svg-png-gif-file-formats--lungs-checkup-medical-pack-healthcare-illustrations-9439248.png?f=webp" alt="Liver" width="500" height="400">
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3, col4, col5,col6 = st.columns([1, 1, 1, 1, 1,1])
        with col2:
            if st.form_submit_button("Login",type='primary'):
                navigate_to_page("login")
        with col5:
            if st.form_submit_button("Sign Up",type='primary'):
                navigate_to_page("signup")
