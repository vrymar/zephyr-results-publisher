import json
import requests
import os

from zephyr_results_publisher.file_util import *
from zephyr_results_publisher.helper import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

BASE_URL = "https://api.zephyrscale.smartbear.com/v2"
API_KEY = str(os.environ.get("API_KEY"))


def publish(project_key, source_report_file, report_format, auto_create_test_cases="true"):
    source_path_dir = get_path_dir(source_report_file)
    output_zip = f"{source_path_dir}/testResults.zip"
    zip_file(source_report_file, output_zip)

    url = BASE_URL + f"/automations/executions/{report_format}"

    params = {
        "projectKey": project_key,
        "autoCreateTestCases": auto_create_test_cases
    }
    headers = {
        "Authorization": "Bearer " + API_KEY
    }
    files = {
        "file": open(output_zip, 'rb')
    }

    response = requests.post(url, files=files, params=params, headers=headers)
    check_response_status(response, 200)
    parsed_response = json.loads(response.text)
    logging.info(f"Parsed response: {parsed_response}")
    return parsed_response


def publish_customized_test_cycle(project_key,
                                  source_report_file,
                                  report_format,
                                  auto_create_test_cases="true",
                                  test_cycle_name="Automated Build",
                                  test_cycle_folder_name="All test cycles",
                                  test_cycle_description="",
                                  test_cycle_jira_project_version=1,
                                  test_cycle_custom_fields=None):
    if test_cycle_custom_fields is None:
        test_cycle_custom_fields = {}
    source_path_dir = get_path_dir(source_report_file)
    output_zip = f"{source_path_dir}/testResults.zip"
    zip_file(source_report_file, output_zip)

    url = BASE_URL + f"/automations/executions/{report_format}"

    test_cycle = customize_test_cycle(project_key,
                                      test_cycle_name,
                                      test_cycle_folder_name,
                                      test_cycle_description,
                                      test_cycle_jira_project_version,
                                      test_cycle_custom_fields)
    params = {
        "projectKey": project_key,
        "autoCreateTestCases": auto_create_test_cases
    }
    headers = {
        "Authorization": "Bearer " + API_KEY
    }
    files = {
        "file": open(output_zip, 'rb'),
        "testCycle": ("test_cycle.json", test_cycle, "application/json")
    }

    response = requests.post(url, files=files, params=params, headers=headers)
    check_response_status(response, 200)
    parsed_response = json.loads(response.text)
    logging.info(f"Parsed response: {parsed_response}")
    return parsed_response


def customize_test_cycle(project_key, test_cycle_name="Automation cycle", folder_name="All test cycles",
                         description="", jira_project_version=1, custom_fields=None):
    if custom_fields is None:
        custom_fields = {}
    folder_id = get_folder_id_by_name(folder_name, project_key, 20)
    test_cycle_json = {
        "name": test_cycle_name,
        "description": description,
        "jiraProjectVersion": jira_project_version,
        "folderId": folder_id,
        "customFields": custom_fields
    }
    logging.info(f"Custom test cycle is generated: {test_cycle_json}")
    return json.dumps(test_cycle_json)


def get_folder_id_by_name(name, project_key, max_results):
    url = BASE_URL + f"/folders"

    params = {
        "projectKey": project_key,
        "folderType": "TEST_CYCLE",
        "startAt": 0,
        "maxResults": max_results
    }
    headers = {
        "Authorization": "Bearer " + API_KEY
    }

    logging.info(params)

    response = requests.get(url, params=params, headers=headers)
    check_response_status(response, 200)
    parsed_response = json.loads(response.text)
    return find_folder_id_by_name(name, parsed_response)