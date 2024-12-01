# @title Env Setup
# !pip install anthropic

# env_setup.py: Module to set up the environment for the ColabAgent.

from google.colab import drive
from googleapiclient.discovery import build

def setup_directory_structure():
    """Set up required directory structure for the ColabAgent."""
    gdrive = GoogleDrive()
    drive.mount('/content/drive')

    colab_agent_dir = gdrive.directory_exists('ColabAgent')
    if not colab_agent_dir:
        raise ValueError("Could not find ColabAgent directory")

    required_dirs = ['prompts', 'chains', 'steps']
    created_dirs = {}

    for dir_name in required_dirs:
        dir_id = gdrive.directory_exists(dir_name, parent_id=colab_agent_dir)
        if not dir_id:
            print(f"Creating {dir_name}/ directory...")
            dir_id = gdrive.create_directory(dir_name, parent_id=colab_agent_dir)
        else:
            print(f"{dir_name}/ directory already exists")
        created_dirs[dir_name] = dir_id

    return created_dirs

def copy_public_prompts(prompts_dir_id: str, public_folder_id: str = "1AYlnc58M0TnMuDTPr4x_bwaJIlSV5-3v"):
    """Copy Google Docs from public folder to prompts directory if they don't already exist."""
    gdrive = GoogleDrive()

    # Get all files from public folder
    files = gdrive.get_files_in_directory(public_folder_id)

    # Filter for Google Docs
    docs = [f for f in files if f['mimeType'] == 'application/vnd.google-apps.document']

    # Copy each doc to prompts directory if it doesn't exist
    for doc in docs:
        if not gdrive.file_exists(doc['name'], parent_id=prompts_dir_id):
            copied_file = gdrive.service.files().copy(
                fileId=doc['id'],
                body={'name': doc['name'], 'parents': [prompts_dir_id]}
            ).execute()
            print(f"Copied {doc['name']} to prompts directory")
        else:
            print(f"Skipped {doc['name']} - already exists in prompts directory")

def copy_public_chains(chains_dir_id: str, public_folder_id: str = "1xhbQNeqWngRoMeughdXwP_pvJkVbyg4c"):
    """Copy Google Docs from public folder to chains directory if they don't already exist."""
    gdrive = GoogleDrive()

    # Get all files from public folder
    files = gdrive.get_files_in_directory(public_folder_id)

    # Filter for Google Docs
    docs = [f for f in files if f['mimeType'] == 'application/vnd.google-apps.document']

    # Copy each doc to chains directory if it doesn't exist
    for doc in docs:
        if not gdrive.file_exists(doc['name'], parent_id=chains_dir_id):
            copied_file = gdrive.service.files().copy(
                fileId=doc['id'],
                body={'name': doc['name'], 'parents': [chains_dir_id]}
            ).execute()
            print(f"Copied {doc['name']} to chains directory")
        else:
            print(f"Skipped {doc['name']} - already exists in chains directory")

def main():
    created_dirs = setup_directory_structure()
    copy_public_prompts(created_dirs['prompts'])
    copy_public_chains(created_dirs['chains'])

if __name__ == "__main__":
    main()