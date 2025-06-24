import os
import configparser
from atlassian import Jira

def read_credentials():
    """Read credentials from the .atlassian-cloud/credentials.properties file"""
    home_dir = os.path.expanduser("~")
    credentials_path = os.path.join(home_dir, ".atlassian-cloud", "credentials.properties")
    
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Credentials file not found at {credentials_path}")
    
    config = configparser.ConfigParser()
    config.read(credentials_path)
    
    if 'atlassian' not in config:
        raise ValueError("No [atlassian] section found in credentials file")
    
    atlassian_config = config['atlassian']
    
    return {
        'instances': [instance.strip() for instance in atlassian_config['instances'].split(',')],
        'username': atlassian_config['username'],
        'api_token': atlassian_config['api_token']
    }

def get_all_jira_projects():
    """Retrieve all projects from all Jira instances"""
    try:
        credentials = read_credentials()
        
        for instance in credentials['instances']:
            jira_url = f"https://{instance}.atlassian.net"
            logging.info(f"\n{instance}")
            logging.info("-" * len(instance))
            
            try:
                # Connect to Jira instance
                jira = Jira(
                    url=jira_url,
                    username=credentials['username'],
                    password=credentials['api_token']
                )
                
                # Get all projects
                projects = jira.projects()
                
                if not projects:
                    print("No projects found or no access to projects")
                    continue
                
                # Sort projects by name for consistent output
                projects.sort(key=lambda x: x.get('name', ''))
                
                for project in projects:
                    project_key = project.get('key', '')
                    project_name = project.get('name', 'Unknown')
                    
                    # Get detailed project information to retrieve the lead
                    try:
                        project_details = jira.project(project_key)
                        project_lead = project_details.get('lead', {}).get('displayName', 'No lead assigned')
                    except Exception as detail_error:
                        print(f"  Warning: Could not get details for project {project_name}: {str(detail_error)}")
                        project_lead = 'No lead assigned'
                    
                    print(f"{project_name}, project lead: {project_lead}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Connection error with {instance}: {str(e)}")
                continue
            except JiraError as e:
                print(f"Jira API error with {instance}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error reading credentials: {str(e)}")

def main():
    print("Retrieving Jira projects from all instances...")
    get_all_jira_projects()

if __name__ == "__main__":
    main()