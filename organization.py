import json
import time
import googleapiclient.discovery
from google.oauth2 import service_account
import functools

MAX_RETRIES = 3

with open("organization.json") as source:
    info = json.load(source)

credentials = service_account.Credentials.from_service_account_info(
    info, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

support_service = googleapiclient.discovery.build(
    serviceName="cloudsupport",
    version="v2beta",
    discoveryServiceUrl="https://cloudsupport.googleapis.com/$discovery/rest?version=v2beta",
    credentials=credentials,
)

# Get project ids
def get_project_ids():

    project_id = []

    # Get projects from the organization
    project_resource = googleapiclient.discovery.build(
        serviceName="cloudresourcemanager", version="v3", credentials=credentials
    )

    project_ids = project_resource.projects().search().execute()

    for project in project_ids.get("projects", []):
        project_id.append(project.get("name"))

    return project_id


# Get cases from each project under the organization
def get_cases_for_project(project_id):
    get_cases = support_service.cases().list(parent=project_id).execute()
    cases = get_cases.get("cases", [])
    return cases


def process_case(case):
    # Checking to see if the case is NOT closed
    if case["state"] == "NEW" or case["state"] == "ASSIGNED":
        return case["name"]
    return None


def support_subscribe_emails(emails):
    project_ids = get_project_ids()

    # Step 1: Map - Get cases for each project using map
    cases_list = map(get_cases_for_project, project_ids)

    # Step 2: Reduce - Flatten the list of cases from multiple projects
    cases = functools.reduce(lambda x, y: x + y, cases_list)

    # Step 3: Map - Process each case to get the case numbers using map
    case_numbers = list(filter(None, map(process_case, cases)))

    # Step 4: Map - Update the CC list for each case using map
    updated_cases = map(
        lambda case_number: update_cc_for_case(case_number, emails), case_numbers
    )

    list(updated_cases)


def update_cc_for_case(case_number, emails):
    # Step 1: Get the case details using support_service.cases().get()
    get_case_req = support_service.cases().get(name=case_number)
    case_details = get_case_req.execute(num_retries=MAX_RETRIES)

    # Step 2: Update the subscriberEmailAddresses (CC) list with the new emails
    if "subscriberEmailAddresses" in case_details:
        current_cc = case_details["subscriberEmailAddresses"]
        current_cc.extend(emails)
    else:
        current_cc = emails

    # Step 3: Make the API call to update the CC list for the case
    body = {"subscriberEmailAddresses": current_cc}
    update_mask = "subscriberEmailAddresses"
    update_req = support_service.cases().patch(
        name=case_number, updateMask=update_mask, body=body
    )
    update_req.execute(num_retries=MAX_RETRIES)


support_subscribe_emails(["email@domain.com"])
