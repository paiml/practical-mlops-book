from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession


url = 'https://us-central1-gcp-book-1.cloudfunctions.net/function-1'


creds = service_account.IDTokenCredentials.from_service_account_file(
       'service-account-credentials.json', target_audience=url)

authed_session = AuthorizedSession(creds)

# make authenticated request and print the response, status_code
import ipdb;ipdb.set_trace()
resp = authed_session.post(url, data='{"message": "hello from the programming language"}')
print(resp.status_code)
print(resp.text)


#import requests
#
#
#METADATA_URL = 'http://metadata.google.internal/computeMetadata/v1/'
#METADATA_HEADERS = {'Metadata-Flavor': 'Google'}
#SERVICE_ACCOUNT = 'default'
#
#
#def get_access_token():
#    url = '{}instance/service-accounts/{}/token'.format(
#        METADATA_URL, SERVICE_ACCOUNT)
#
#    # Request an access token from the metadata server.
#    r = requests.get(url, headers=METADATA_HEADERS)
#    r.raise_for_status()
#
#    # Extract the access token from the response.
#    access_token = r.json()['access_token']
#
#    return access_token
#
#print(get_access_token())
