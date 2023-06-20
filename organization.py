import requests
import json
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

MAX_RETRIES = 3

with open('organization.json') as source:
    info = json.load(source)

credentials = service_account.Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/cloud-platform'])

# Get our discovery doc and build our service
support_service = googleapiclient.discovery.build(
                            serviceName="cloudsupport",
                            version="v2beta",
                            discoveryServiceUrl="https://cloudsupport.googleapis.com/$discovery/rest?version=v2beta",
                            credentials=credentials)

project_resource = googleapiclient.discovery.build(
                            serviceName="cloudresourcemanager",
                            version="v3",
                            credentials=credentials)

def get_project_ids():
    project_id = []
    # Get projects from the organization
    project_ids = project_resource.projects().search().execute()
    for project in project_ids.get('projects', []):
        project_id.append(project.get('name'))
    
    return project_id

def support_subscribe_emails(emails):
    
    project_ids = get_project_ids()

    for project_id in project_ids:
        parent = project_id 

        get_cases = support_service.cases().list(parent=parent).execute()

        for case in get_cases['cases']:
            # Case number
            case_number = case['name']

            get_case_req = support_service.cases().get(name=case_number)
    
            case_details = get_case_req.execute(num_retries=MAX_RETRIES)
            new_cc = emails
            
            if "subscriberEmailAddresses" in case_details:
                current_cc = case_details["subscriberEmailAddresses"]
                # List of added emails not already in CC list for notifications
                new_cc = [x for x in emails if x not in current_cc]
                # Update list
                emails.extend(current_cc)

                # Update CC list
                update_email(emails, case_number)

            # If subscriberEmailAddresses is not present (no CC in the case)
            elif "subscriberEmailAddresses" not in case_details:
                # Create CC list with emails
                update_email(emails, case_number)

def update_email(emails, case_number):
    # Update CC list
    body = {"subscriberEmailAddresses": [emails]}
    update_mask = "subscriberEmailAddresses"
    update_req = support_service.cases().patch(name=case_number, updateMask=update_mask, body=body)
    update_req.execute(num_retries=MAX_RETRIES)

support_subscribe_emails(['taufique@nooranillc.com'])