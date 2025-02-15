# hubspot.py

#imports
import json
import secrets
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
import base64
import requests
from integrations.integration_item import IntegrationItem
import time
from redis_client import add_key_value_redis, get_value_redis, delete_key_redis

#import dotenv and to use environment variables and secrets
from dotenv import load_dotenv
import os

#load env
load_dotenv()

#Required variables from env
CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID")
CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET")
REQUIRED_SCOPES = os.getenv("REQUIRED_SCOPES")
REDIRECT_URI = os.getenv('HUBSPOT_REDIRECT_URI')
AUTHORIZATION_DOMAIN = os.getenv("HUBSPOT_AUTHORIZATION_URL")
API_DOMAIN = os.getenv("HUBSPOT_API_DOMAIN")

#Required URLs
authorization_url = f'{AUTHORIZATION_DOMAIN}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}'
access_token_url = f'{API_DOMAIN}/oauth/v1/token'
get_items_hubspot_url = f'{API_DOMAIN}/crm/v3/objects/0-2' #company id

#Initial authorization for Hubspot 
async def authorize_hubspot(user_id, org_id):
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = json.dumps(state_data)
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', encoded_state, expire=600)

    #REFERENCE : https://developers.hubspot.com/docs/guides/apps/authentication/oauth-quickstart-guide#step-1-create-the-authorization-url-and-direct-the-user-to-hubspot-s-oauth-2.0-server
    return f'{authorization_url}&scope={REQUIRED_SCOPES}&state={encoded_state}'

#get the credentials and store
async def oauth2callback_hubspot(request: Request):
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error'))
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state').replace('\\\"', '"').replace('+','')
    state_data = json.loads(encoded_state)

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')

    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')

    #REFERENCE : https://developers.hubspot.com/docs/guides/apps/authentication/oauth-quickstart-guide#step-4-exchange-authorization-code-for-tokens
    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                access_token_url,
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': REDIRECT_URI,
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET
                }, 
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                }
            ),
            delete_key_redis(f'hubspot_state:{org_id}:{user_id}'),
        )
    
    credentials = response.json()

    #update expires_in to token expiration time
    credentials["expires_in"] = time.time() + credentials['expires_in']

    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(credentials), expire=1800)

    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

#get hubspot credentials
async def get_hubspot_credentials(user_id, org_id):
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    credentials = json.loads(credentials)
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')

    return credentials

#check if access token is expired
def is_token_expired(expires_in):
    return time.time() >= expires_in

#refresh access token if expired
async def refresh_access_token(credentials):
    data = {
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': credentials['refresh_token']
    }

    #REFERENCE : https://developers.hubspot.com/docs/guides/apps/authentication/oauth-quickstart-guide#refreshing-oauth-2.0-tokens
    response = requests.post(access_token_url, data)
    credentials = response.json()
    credentials['expires_in'] = time.time() + credentials['expires_in']
    return credentials

#create integration item
def create_integration_item_metadata_object(result):
    #item properties
    result_properties = result["properties"]

    integration_item_metadata = IntegrationItem(
        id = result_properties["hs_object_id"],
        parent_id = result["id"],
        type = "company",
        name = result_properties["name"],
        creation_time = result["createdAt"],
        last_modified_time = result["updatedAt"],
        url = result_properties["domain"]
    )

    return integration_item_metadata

#get items from hubspot
async def get_items_hubspot(credentials):
    credentials = json.loads(credentials)
    
    #refresh token if expired
    if is_token_expired(credentials.get("expires_in")):
        credentials = await refresh_access_token(credentials)
    
    list_of_integration_item_metadata = []

    #REFERENCE : https://developers.hubspot.com/docs/guides/api/crm/using-object-apis#retrieve-records
    response = requests.get(
        get_items_hubspot_url,
        headers={
            'Authorization': f'Bearer {credentials.get("access_token")}'
        },
        params={
            'properties': 'name,domain,city,industry,phone,state'
        }
    )

    response = response.json()
    results = response["results"]

    for result in results:
        integration_item = create_integration_item_metadata_object(result)
        list_of_integration_item_metadata.append(integration_item)

    return list_of_integration_item_metadata