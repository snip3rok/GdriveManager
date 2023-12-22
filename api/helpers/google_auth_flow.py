import google_auth_oauthlib.flow

import config

client_config = {
    'web': {
        'client_id': config.GOOGLE_CLIENT_ID,
        'client_secret': config.GOOGLE_CLIENT_SECRET,
        'redirect_uris': ['urn:ietf:wg:oauth:2.0:oob'],
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://accounts.google.com/o/oauth2/token',
        'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
    }
}

# Create a flow using client_config
flow = google_auth_oauthlib.flow.Flow.from_client_config(
    client_config,
    scopes=config.SCOPES,
)

flow.redirect_uri = 'http://localhost:8000/auth'

authorization_url, state = flow.authorization_url(
    access_type='offline',
    include_granted_scopes='true')
