import streamlit as st
import requests
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs

# Define your OAuth credentials and endpoints
CLIENT_ID = 'your-client-id'
CLIENT_SECRET = 'your-client-secret'
REDIRECT_URI = 'http://localhost:8501'
AUTH_URL = 'https://your-tableau-server/oauth2/authorize'
TOKEN_URL = 'https://your-tableau-server/oauth2/token'

# Function to generate the OAuth authorization URL
def get_auth_url():
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'tableau:views:embed'  # Adjust scope as needed
    }
    return f"{AUTH_URL}?{urlencode(params)}"

# Function to retrieve OAuth token
def get_oauth_token(auth_code):
    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(TOKEN_URL, data=payload)
    response_data = response.json()
    return response_data.get('access_token')

# Streamlit app
st.title("Login to Tableau")

# Check if the user is already authenticated
if 'access_token' not in st.session_state:
    st.write("Please log in to access the app.")

    # Create a login button
    if st.button('Log In with Tableau'):
        # Redirect to the OAuth authorization URL
        auth_url = get_auth_url()
        webbrowser.open(auth_url)
    
    # Get the authorization code from the URL
    parsed_url = urlparse(st.experimental_get_query_params().get('url', [''])[0])
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
