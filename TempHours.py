

import requests
import argparse
import configparser
import os
import warnings
import pandas as pd
from glob import glob
from sys import exit
from datetime import date, timedelta

config = configparser.ConfigParser()
if config.read('config.ini') != ['config.ini']:
    config['User'] = {} 
    config['Token'] = {}
    config['User']['Email'] = input('Jira Email Address: ')
    print('You can obtain a Tempo token from:https://helpsystems.atlassian.net/plugins/servlet/ac/io.tempo.jira/tempo-app#!/configuration/api-integration')
    config['Token'] ['Tempo'] = input('Tempo Token: ')
    print('You can obtain a Jira token from: https://id.atlassian.com/manage-profile/security/api-tokens')
    config['Token'] ['Jira'] = input('Jira Token: ')
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

my_email = '' #put your email address. This email address should have write permissions to the Jira
tempo_token= '' #fetch tempo token from Tempo
jira_token= '' #fetch jira token from Jira


##CONSTANTS##
TEMPO_BASEURL= 'https://api.tempo.io/4'
JIRA_BASEURL = 'https://<your org name>.atlassian.net/rest/api/3'

TEMPO_WORKLOGS = '/worklogs'
JIRA_USER = '/user/search'
JIRA_PROJECT = '/project'
JIRA_ISSUE = '/issue'

DEFAULT_TD = 'WHT-3'
DEFAULT_TO = 'WHT-2'
DEFAULT_OT = 'WHT-1'

headers = {
'Accept': 'application/json'
}
jira_headers = headers.copy()
tempo_headers = headers.copy()

tempo_headers['Authorization'] = f'Bearer {tempo_token}'
jira_auth = requests.auth.HTTPBasicAuth(my_email, jira_token)

##FUNCTIONS##


def get_user_id(email):
    response = requests.get(f' (JIRA_BASEURL) (JIRA_USER)', params='query=%s' % email, auth=jira_auth, headers=jira_headers)
    return response.json()[0]['accountId']


def get_issue_id(issue):
    response = requests.get(f' (JIRA_BASEURL) (JIRA_ISSUE)/(issue)', auth=jira_auth, headers=jira_headers)
    return response.json()['id']


def post_worklog(user_id, issue_id, start_date, time, category):

    time *=3600

    params = {
        'authorAccountId': user_id,
        'issueId': issue_id,
        'startDate': start_date.isoformat(),
        'timeSpentSeconds' : time,
        'attributes' : [
            {
                'key' : '_WorkCategory_',
                'value': category
            }
        ]
    }

    try:
        response = requests.post(f'{TEMPO_BASEURL} {TEMPO_WORKLOGS}', json=params, headers=tempo_headers)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: (err)")
    except:
        return 500
    return response.status_code


def process_file(filename):

    today_date = date.today()

    #Subtract 3 days from today
    today_date = today_date - timedelta(days=10)
    #date.today().strftime('%Y-%m-%d')

    file_path = 'C:\\Coding\\python\\FinalHours.xlsx'
    df = pd.read_excel(file_path)
    columns = df.columns

    for row_index in range(len (df)):
        user_email = get_cell_value(df, 'email', row_index)
        user_id = get_user_id(user_email)
        
        user_issue = get_cell_value(df, 'issue_id', row_index)
        issue_id = get_issue_id(user_issue)
        otherIssueId = get_issue_id('WHT-5')
        
        user_hours = float(get_cell_value(df, 'Feature Planning', row_index))
        if pd.notna (user_hours):
            post_worklog(user_id, issue_id, today_date, user_hours, 'RDR')
        
        user_hours = float(get_cell_value (df, 'Project Management', row_index))
        if pd.notna(user_hours):
            post_worklog(user_id, issue_id, today_date, user_hours, 'PMA')

        user_hours = float(get_cell_value (df, 'Feature Development', row_index))
        if pd.notna (user_hours): 
            post_worklog(user_id, issue_id, today_date, user_hours, 'FW')

        user_hours = float(get_cell_value (df, 'Tech Debt', row_index))
        if pd.notna (user_hours):
            post_worklog(user_id, otherIssueId, today_date, user_hours, 'TD')
    
        user_hours = float(get_cell_value (df, 'Customer Support', row_index))
        if pd.notna (user_hours):
            post_worklog(user_id, otherIssueId, today_date, user_hours, 'TD')
        
        user_hours = float(get_cell_value (df, 'Infrastructure', row_index))
        if pd.notna (user_hours):
            post_worklog (user_id, issue_id, today_date, user_hours, 'MW')
        
        user_hours = float(get_cell_value (df, 'Time Off', row_index))
        if pd.notna (user_hours):
            post_worklog(user_id, otherIssueId, today_date, user_hours, 'TO')
        
        user_hours = float(get_cell_value(df, 'Bank Holiday', row_index))
        if pd.notna(user_hours):
            post_worklog(user_id, otherIssueId, today_date, user_hours, 'TO')
        
        user_hours = float(get_cell_value (df, 'Other', row_index))
        if pd.notna(user_hours):
            post_worklog(user_id, otherIssueId, today_date, user_hours, 'OT')
        

def get_cell_value(df, column_name, row_index):
    if column_name in df.columns and 0 <= row_index < len (df):
        return df.at[row_index, column_name]
    else:
        return 0


##MAIN CODE##
if __name__ == '__main__':
    process_file("temp file")