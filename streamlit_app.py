import streamlit as st
import os

# Initialize the session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login function
def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()

# Logout function
def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

# Define pages
login_page = st.Page(login, title="Customer Contact Center Demo", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

self_service_page = st.Page("SelfServiceBot.py", title="Self Service Chatbot", icon="🧊")
ai_assisted_page = st.Page("AiAssistedBot.py", title="AI Assisted Chatbot", icon="🧊")

# Set the page configuration
st.set_page_config(page_title="Customer Contact Center Demo", page_icon="🧊", layout="wide")

# Show customer sign-in dropdown
if not st.session_state.logged_in:
    st.title("Azure OpenAI powered Contact Center")
    with st.container():
        st.markdown('<div class="fixed-dropdown">', unsafe_allow_html=True)
        Customer_Name = st.selectbox("Sign in as:", 
                                    ["Alex Richardson", 
                                    "David Newman",
                                    "Paula Smith",
                                    "Wendy Miller",
                                    "Yvonne Davis"], index=0)
        st.markdown('</div>', unsafe_allow_html=True)
    # Assign customer_id based on the selected name
    if Customer_Name == "Alex Richardson":
        customer_id = 1
    elif Customer_Name == "David Newman":
        customer_id = 2
    elif Customer_Name == "Paula Smith":
        customer_id = 3
    elif Customer_Name == "Wendy Miller":
        customer_id = 4
    else:
        customer_id = 5
    st.session_state.customer_id = customer_id


    # Navigation based on login state
if st.session_state.logged_in:
    pg = st.navigation([self_service_page, ai_assisted_page])
else:
    pg = st.navigation([login_page])
pg.run()

if st.session_state.logged_in == False:

    # Layout with one column for logo and radio buttons
    col1, col2 = st.columns([5, 1])

    with col1:
        # Mapping company names to logo filenames
        companies = ["Coca&Cola", "Danone", "Kellogg's", "Kraft Heinz", "Mondelez", "Nestlé", "Unilever"]
        logo_mapping = {
            "Coca&Cola": "CocaCola.png",
            "Danone": "Danone.png",
            "Kellogg's": "Kelloggs.png",
            "Kraft Heinz": "KraftHeinz.png",
            "Mondelez": "Mondelez.png",
            "Nestlé": "Nestle.png",
            "Unilever": "Unilever.png"
        }
        company = st.radio("Select a company:", companies, horizontal=True)

    with col2:
        # Set a fixed height container for the logo
        logo_filename = logo_mapping.get(company)
        if logo_filename:
            # Get the current directory of the script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(base_dir, f"logos/{logo_filename}")
            # Display the image inside the fixed height container
            st.image(logo_path, width=100)


