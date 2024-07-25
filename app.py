import streamlit as st
import requests
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs

# Streamlit app
st.title("Tableau Dashboard Integration")

# Check if OAuth credentials are already set
if 'client_id' not in st.session_state:
    st.session_state['client_id'] = ''
if 'client_secret' not in st.session_state:
    st.session_state['client_secret'] = ''
if 'redirect_uri' not in st.session_state:
    st.session_state['redirect_uri'] = ''
if 'auth_url' not in st.session_state:
    st.session_state['auth_url'] = ''
if 'token_url' not in st.session_state:
    st.session_state['token_url'] = ''

# Configuration form
st.header("Configuration")
with st.form("config_form"):
    client_id = st.text_input('Client ID', st.session_state['client_id'])
    client_secret = st.text_input('Client Secret', st.session_state['client_secret'], type='password')
    redirect_uri = st.text_input('Redirect URI', st.session_state['redirect_uri'], value='http://localhost:8501')
    auth_url = st.text_input('Authorization URL', st.session_state['auth_url'])
    token_url = st.text_input('Token URL', st.session_state['token_url'])
    submit_button = st.form_submit_button(label='Save Configuration')

if submit_button:
    st.session_state['client_id'] = client_id
    st.session_state['client_secret'] = client_secret
    st.session_state['redirect_uri'] = redirect_uri
    st.session_state['auth_url'] = auth_url
    st.session_state['token_url'] = token_url
    st.success("Configuration saved successfully!")

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

# Authentication section
st.header("Login to Tableau")

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

