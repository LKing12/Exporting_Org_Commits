# Exporting_Org_Commits

This script fetches every commit from all repositories in a GitHub organization, grouped by user, and generates an Excel file with an overview sheet and one sheet per committer.

## Variables at the Top of `main.py`
Before running the script, you need to configure the following variables at the top of `main.py`:

- `USERNAME`: Your GitHub username (e.g., `'LKing12'`).
- `TOKEN`: Your GitHub Personal Access Token (classic). See the section below for required scopes. (e.g., `'ghp_yourtokenvalue'`)
- `START_DATE`: The beginning of the date range for fetching commits (e.g., `'2024-01-01T00:00:00Z'`).
- `END_DATE`: The end of the date range for fetching commits (e.g., `'2024-01-31T23:59:59Z'`).
- `ORG_NAME`: The exact name of the GitHub organization you want to export commits from (e.g., `'microsoft'`).
- `repos`: A Python list of strings, where each string is the name of a specific repository within the organization from which to fetch commits (e.g., `['vscode', 'playwright']`). The script will iterate through this list to get commits from each specified repository.

## Output
- **Overview sheet:** Summary of all commits across repos and users.
- **One sheet per committer:** Detailed commit info for each user.

## Sheet Details and Column Descriptions

### Overview Sheet
This sheet provides a unique list of committers and the repositories/branches they have contributed to.
- `author_name`: The name of the commit author.
- `author_email`: The email address of the commit author.
- `repo`: The name of the repository.
- `branch`: The name of the branch.

### Committer Sheets (One per User)
These sheets contain detailed information for every commit made by a specific user.
- `repo`: The name of the repository where the commit was made.
- `branch`: The name of the branch where the commit was made.
- `message`: The commit message.
- `author_name`: The name of the commit author.
- `author_email`: The email address of the commit author.
- `author_date`: The date and time the commit was authored (converted to Australian Eastern Standard Time - AEST, and timezone information removed for Excel compatibility).
- `url`: The URL to the commit on GitHub.
- `start_of_week`: The date of the Monday of the week the commit was authored (calculated from `author_date`).

## Getting a GitHub Personal Access Token
Generate a **Personal Access Token (classic)** at [https://github.com/settings/tokens](https://github.com/settings/tokens/new).
The following scopes are required for the script to function correctly:
- **`repo`**: Grants full control of private repositories and read access to public repositories. Essential for accessing commit history and branch information.
- **`user`**
    - `read:user`: Grants access to read a user's profile data.
    - `user:email`: Grants access to read a user's email addresses.
- **`read:org`** (Recommended): Grants read access to organization membership, projects, and team membership. Useful if you intend to modify the script to list all repositories within an organization automatically.
