import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz
import xlsxwriter

# Replace with your GitHub username, token, and organization
USERNAME = 'LKing12'  # Your GitHub username
TOKEN = ''  # Your GitHub Personal Access Token with 'repo' scope

START_DATE = '2024-12-16T00:00:00Z'  # The start date for fetching commits
END_DATE = '2025-02-22T23:59:59Z'    # The end date for fetching commits

ORG_NAME = ''  # The name of the GitHub organization you want to export commits from
repos = ['','','']  # A list of specific repository names within the organization to fetch commits from. If empty, it will attempt to fetch from all repos (not currently implemented in get_repos).


def get_repos(org_name):
    url = f'https://api.github.com/orgs/{org_name}/repos'
    response = requests.get(url, auth=(USERNAME, TOKEN))
    response.raise_for_status()
    return [repo['name'] for repo in response.json()]

def get_branches(repo_name):
    url = f'https://api.github.com/repos/{ORG_NAME}/{repo_name}/branches'
    response = requests.get(url, auth=(USERNAME, TOKEN))
    response.raise_for_status()
    return [branch['name'] for branch in response.json()]

def get_commits(repo_name, branch_name, start_date, end_date):
    url = f'https://api.github.com/repos/{ORG_NAME}/{repo_name}/commits'
    commits = []
    page = 1
    while True:
        response = requests.get(url, params={'sha': branch_name, 'page': page, 'per_page': 100, 'since': start_date, 'until': end_date}, auth=(USERNAME, TOKEN))
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        for commit in data:
            commit_details = {
                'repo': repo_name,
                'branch': branch_name,
                'message': commit['commit']['message'],
                'author_name': commit['commit']['author']['name'],
                'author_email': commit['commit']['author']['email'],
                'author_date': commit['commit']['author']['date'],
                'url': commit['html_url'],
            } 
            commits.append(commit_details)
        page += 1
    return commits

def get_start_of_week(date):
    date_obj = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    start_of_week = date_obj - timedelta(days=date_obj.weekday())
    return start_of_week.strftime('%Y-%m-%d')

def sanitize_sheet_name(name):
    invalid_chars = '[]:*?/\\'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name[:31]  

all_commits = []

for repo in repos:
    branches = get_branches(repo)
    for branch in branches:
        all_commits.extend(get_commits(repo, branch, START_DATE, END_DATE))

df = pd.DataFrame(all_commits)
df['author_date'] = pd.to_datetime(df['author_date'])

# Convert to AEST
aest = pytz.timezone('Australia/Sydney')
df['author_date'] = df['author_date'].dt.tz_convert(aest).dt.tz_localize(None)

df['start_of_week'] = df['author_date'].apply(lambda x: get_start_of_week(x.strftime('%Y-%m-%dT%H:%M:%SZ')))

committer_dict = {}
if not df.empty:
    df['temp_committer_key'] = df['author_name'].astype(str) + '_' + df['author_email'].astype(str)
    for committer_key_grouped, group in df.groupby('temp_committer_key'):
        committer_dict[committer_key_grouped] = group.drop(columns=['temp_committer_key']).copy()
elif 'author_name' in df.columns and 'author_email' in df.columns: # Handle empty df with columns
    df['temp_committer_key'] = pd.Series(dtype='object')


try:
    with pd.ExcelWriter(
        'github_commits.xlsx', 
        engine='xlsxwriter',
        date_format='yyyy-mm-dd',        
        datetime_format='yyyy-mm-dd hh:mm:ss' 
    ) as writer:
        # Overview sheet
        if not df.empty:
            overview_data = df[['author_name', 'author_email', 'repo', 'branch']].drop_duplicates()
        else: 
            overview_columns = ['author_name', 'author_email', 'repo', 'branch']
            if all(col in df.columns for col in overview_columns):
                overview_data = pd.DataFrame(columns=overview_columns)
            else: 
                overview_data = pd.DataFrame(columns=['author_name', 'author_email', 'repo', 'branch'])
        overview_data.to_excel(writer, sheet_name='Overview', index=False)
        
        # Sheets for each committer
        for committer_key_excel, committer_df_excel in committer_dict.items():
            committer_name = sanitize_sheet_name(committer_key_excel)
            print(f"Creating sheet for {committer_name}")
            committer_df_excel.to_excel(writer, sheet_name=committer_name, index=False)

    print("Excel file created successfully.")
except Exception as e:
    print(f"An error occurred while creating the Excel file: {e}")

print(f"Total number of commits: {len(df)}")
print(f"Number of unique committers: {len(committer_dict)}")
for committer_key, committer_df in committer_dict.items():
    print(f"Committer: {committer_key}, Number of commits: {len(committer_df)}")