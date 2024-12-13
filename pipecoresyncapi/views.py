from django.shortcuts import render
import requests
from .models import *
from apscheduler.schedulers.background import BackgroundScheduler

################################################################################################
# view functions
################################################################################################

def index(request):
    return render(request, 'pipecoresyncapi/index.html')

######################################################################################################
# Procore api credentials
######################################################################################################

# Procore Live credentials
# PROCORE_OAUTH_URL = 'https://login.procore.com'
# PROCORE_BASE_URL = 'https://api.procore.com'
# PROCORE_CLIENT_ID = '5rS90FEAbiPh5pLcZ0sb9XIOsh-HXSVwWiC4LCsnjCc'
# PROCORE_CLIENT_SECRET = 'T9rAtTwXy4izPne1Tm0wK4iBNH7Dn9-I_cCwBgoR338'
# PROCORE_REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# Procore Monthly sandbox credentials
PROCORE_OAUTH_URL = 'https://login-sandbox-monthly.procore.com'
PROCORE_BASE_URL = 'https://api-monthly.procore.com'
PROCORE_CLIENT_ID = '5rS90FEAbiPh5pLcZ0sb9XIOsh-HXSVwWiC4LCsnjCc'
PROCORE_CLIENT_SECRET = 'T9rAtTwXy4izPne1Tm0wK4iBNH7Dn9-I_cCwBgoR338'
PROCORE_REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# Procore sandbox credentials
# PROCORE_OAUTH_URL = 'https://login-sandbox.procore.com'
# PROCORE_BASE_URL = 'https://sandbox.procore.com'
# PROCORE_REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
# PROCORE_CLIENT_ID = 'qwSOYvylfs6AAw49R8fAwZgaQ64NrEzXnJxoWle5v3A'
# PROCORE_CLIENT_SECRET = 'uMRopa0qJ0dBrO4q3B5kf5zNSaq4P4O7CF3etm6kFe4'

######################################################################################################
# Procore API helper functions
######################################################################################################

# function to get fresh access token from Procore whenever needed
def get_procore_acess_token():
    '''
    function to get the access token from Procore for 'client credentials' Auth type.
    '''
    post_data = {
        "client_id": PROCORE_CLIENT_ID,
        "client_secret": PROCORE_CLIENT_SECRET,
        "grant_type": "client_credentials",
        "redirect_uri": PROCORE_REDIRECT_URI
    }
    url = f"{PROCORE_OAUTH_URL}/oauth/token"
    response = requests.post(url, params=post_data)
    # print(response)
    response_json = response.json()
    # created_at = response_json['created_at']
    # expires_in = response_json['expires_in']
    access_token = response_json['access_token']
    # print(access_token)
    return access_token

# Function to get our company id based on access token whenever needed
def get_procore_company_id():
    '''
    function to get the company id from Procore for API requests. 
    '''
    access_token = get_procore_acess_token()
    url = f"{PROCORE_BASE_URL}/rest/v1.0/companies"
    headers = {
        "Authorization": "Bearer " + access_token
    }
    response = requests.get(url, headers=headers)
    response_json = response.json()
    # print(response_json)
    company_id = response_json[0]['id']
    return company_id

################################################################################################
# Pipedrive-Procore API functions
################################################################################################

PIPDRIVE_BASE_URL = 'https://api.pipedrive.com/api/v1'

# {'id': 562949953901854, 'name': 'OSS Project Template'}

def create_project_on_procore_from_pipdrive_deals():
    '''
    function to get all deals from Pipedrive for a specific stage.
    Then gets deal details from Pipedrive and saves required information to database
    '''
    url = f"{PIPDRIVE_BASE_URL}/deals"
    headers = {
        'x-api-token' : 'dc30c4fa2e50974fbd207fe27b1dc54953559dca',
    }
    params = {
        'stage_id' : 7
    }
    response = requests.get(url, headers=headers, params=params) 
    # print(response)
    data = response.json()
    # print(data['data'])
    for deal in data['data']:
        # pipedrive_deal = PipdriveDeals()
        deal_id = deal['id']
        deal_name = deal['person_id']['name']
        deal_address = deal['3ef862ab794499cf7ebc41d2dafc420787df9636']
        deal_zip_code = deal['542c51363940912093cf36ca4d2fb308e1ca63db']
        deal_email_address = deal['person_id']['email'][0]['value']
        deal_phone_number = deal['person_id']['phone'][0]['value']
        deals_names_in_db = PipdriveDeals.objects.values_list('deal_name', flat=True)
        deals_email_address_in_db = PipdriveDeals.objects.values_list('deal_email_address', flat=True)
        if deal_name not in deals_names_in_db and deal_phone_number not in deals_email_address_in_db:
            access_token = get_procore_acess_token()
            company_id = get_procore_company_id()
            url = f"{PROCORE_BASE_URL}/rest/v1.0/projects"
            headers = {
                "Procore-Company-Id" : str(company_id),
                "Authorization": "Bearer " + access_token,
                "Content-Type": "application/json"
            }
            data = {
                    "company_id": str(company_id),
                    "project": {
                        "name": deal_name + " - " + deal_address + " " + str(deal_zip_code),
                        "country_code": 'IE',
                        "address": deal_address,
                        "zip": deal_zip_code,
                        "inbound_email_address": deal_email_address,
                        "phone": deal_phone_number,
                        "project_template_id": 562949953901854, 
                    }
                }
            response = requests.post(url, headers=headers, json=data)
            # print(response)
            response_json = response.json()
            # print(response_json)
            if response.status_code == 201:
                pipedrive_deal = PipdriveDeals()
                pipedrive_deal.deal_id = deal_id
                pipedrive_deal.deal_name = deal_name
                pipedrive_deal.deal_address = deal_address
                pipedrive_deal.deal_zip_code = deal_zip_code
                pipedrive_deal.deal_email_address = deal_email_address
                pipedrive_deal.deal_phone_number = deal_phone_number
                pipedrive_deal.save()
        # print(deal_id)                                                                                                  
            
# create_project_on_procore_from_pipdrive_deals()
    
# def get_all_stages_from_pipedrive():
#     url = f"{BASE_URL}/stages"
#     headers = {
#         'x-api-token' : 'dc30c4fa2e50974fbd207fe27b1dc54953559dca',
#     }
#     response = requests.get(url, headers=headers) 
#     print(response)
#     print(response.json())

# get_all_stages()

# def get_project_templates_from_procore():
#     '''
#     function to get all project templates from Procore
#     '''
#     access_token = get_procore_acess_token()
#     company_id = get_procore_company_id()
#     url = f"{PROCORE_BASE_URL}/rest/v1.0/project_templates"
#     headers = {
#         "Procore-Company-Id" : str(company_id),
#         "Authorization": "Bearer " + access_token,
#         "Content-Type": "application/json"
#     }
#     data = {
#         "company_id" : str(company_id)
#     }
#     response = requests.get(url, headers=headers, params=data)
#     print(response)
#     print(response.json())

# get_project_templates_from_procore()

################################################################################################
# End of Pipdrive functions
################################################################################################


#######################################################################################################
# Scheduling functions to keep DB uptodate
#######################################################################################################

scheduler = BackgroundScheduler()
scheduler.add_job(lambda: create_project_on_procore_from_pipdrive_deals(), 'cron', hour=23)

# scheduler.add_job(lambda: create_project_on_procore_from_pipdrive_deals(), 'cron', minute=1)
# scheduler.add_job(lambda: clean_db_for_fresh_statuses(), 'cron', hour=23)
# scheduler.add_job(lambda: get_all_active_whs_projects(), 'cron', hour=23)
# scheduler.add_job(lambda: get_lov_entries_statuses(), 'cron', hour=23)
# scheduler.add_job(lambda: save_company_stages(), 'cron', hour=23)s
# scheduler.add_job(lambda: get_all_generic_tools(), 'cron', hour=23)
# scheduler.add_job(lambda: get_generic_tool_statuses(), 'cron', hour=23)

# scheduler.add_job(lambda : scheduler.print_jobs(),'interval', seconds=120) 

scheduler.start()

#######################################################################################################
# The End 
#######################################################################################################
