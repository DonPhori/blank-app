import streamlit as st
import requests
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs

# Initialize session state
if 'client_id' not in st.session_state:
    st.session_state['client_id'] = ''
if 'client_secret' not in st.session_state:
    st.session_state['client_secret'] = ''
if 'redirect_uri' not in st.session_state:
    st.session_state['redirect_uri'] = 'http://localhost:8501'
if 'auth_url' not in st.session_state:
    st.session_state['auth_url'] = 'https://your-tableau-server/oauth2/authorize'
if 'token_url' not in st.session_state:
    st.session_state['token_url'] = 'https://your-tableau-server/oauth2/token'
if 'access_token' not in st.session_state:
    st.session_state['access_token'] = None

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Sign Up", "Log In"])

# Function to generate the OAuth authorization URL
def get_auth_url():
    params = {
        'response_type': 'code',
        'client_id': st.session_state['client_id'],
        'redirect_uri': st.session_state['redirect_uri'],
        'scope': 'tableau:views:embed'  # Adjust scope as needed
    }
    return f"{st.session_state['auth_url']}?{urlencode(params)}"

# Function to retrieve OAuth token
def get_oauth_token(auth_code):
    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': st.session_state['redirect_uri'],
        'client_id': st.session_state['client_id'],
        'client_secret': st.session_state['client_secret']
    }
    response = requests.post(st.session_state['token_url'], data=payload)
    response_data = response.json()
    return response_data.get('access_token')

# Sign Up Page
if page == "Sign Up":
    st.title("Sign Up - Configure OAuth Settings")
    
    st.session_state['client_id'] = st.text_input("Client ID", value=st.session_state['client_id'])
    st.session_state['client_secret'] = st.text_input("Client Secret", type="password", value=st.session_state['client_secret'])
    st.session_state['auth_url'] = st.text_input("Authorization URL", value=st.session_state['auth_url'])
    st.session_state['token_url'] = st.text_input("Token URL", value=st.session_state['token_url'])
    st.session_state['redirect_uri'] = st.text_input("Redirect URI", value=st.session_state['redirect_uri'])

    if st.button("Save Configuration"):
        st.write("Configuration saved successfully! Switch to the Log In page to authenticate users.")

# Log In Page
elif page == "Log In":
    st.title("Log In to Tableau")

    # Check if the user is already authenticated
    if 'access_token' not in st.session_state or st.session_state['access_token'] is None:
        st.write("Please log in to access the app.")

        # Create a login button
        if st.button('Log In with Tableau'):
            # Redirect to the OAuth authorization URL
            auth_url = get_auth_url()
            webbrowser.open(auth_url)

        # Get the authorization code from the URL
        query_params = st.query_params
        if 'url' in query_params:
            parsed_url = urlparse(query_params['url'][0])
            auth_code = parse_qs(parsed_url.query).get('code', [None])[0]

            if auth_code:
                # Exchange the authorization code for an access token
                access_token = get_oauth_token(auth_code)
                if access_token:
                    st.session_state['access_token'] = access_token
                    st.write("You are now logged in!")
                else:
                    st.write("Failed to obtain access token.")
    else:
        st.write("You are already logged in!")

        # Display a placeholder for the dashboard or other content
        st.write("Welcome! You can now view the Tableau dashboards.")
        # Add your code here to display Tableau dashboards or other content

        # Example: Input for Tableau dashboard URL with default value
        default_url = 'https://your-tableau-server/views/YourDashboard/Sheet1'
        dashboard_url = st.text_input('Enter the Tableau dashboard URL:', value=default_url)

        if dashboard_url:
            st.components.v1.html(
                f"""
                <script type="module" src="https://public.tableau.com/javascripts/api/tableau.embedding.3.latest.min.js"></script>
                <script>
                    document.addEventListener("DOMContentLoaded", function() {{
                        var containerDiv = document.getElementById("tableauViz");
                        var url = "{dashboard_url}";
                        var options = {{
                            hideTabs: true,
                            width: "1000px",
                            height: "800px",
                            token: "{st.session_state['access_token']}" // Pass the OAuth token if needed
                        }};
                        var viz = new tableau.Viz(containerDiv, url, options);
                    }});
                </script>
                <div id="tableauViz"></div>
                """,
                height=800,
            )
