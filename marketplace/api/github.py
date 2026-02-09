import re
import base64
import frappe
import requests
from frappe import _
from frappe.utils.oauth import get_oauth2_authorize_url

# Helpers

def get_connected_app():
    connected_app_name = frappe.db.get_value(
        "Connected App",
        {"provider_name": "Github"},
        "name"
    )
    if not connected_app_name:
        frappe.throw(_("Marketplace Connected App not found."))

    return frappe.get_doc("Connected App", connected_app_name)


def get_github_token():
    connected_app = get_connected_app()
    token_cache = connected_app.get_token_cache(frappe.session.user)

    if not token_cache:
        frappe.throw(_("No token found. Please authorize GitHub."))

    return token_cache.get_password("access_token")


def get_github_headers():
    token = get_github_token()
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }


# OAuth / Login

@frappe.whitelist(allow_guest=True)
def get_github_login_url():
    return get_oauth2_authorize_url("github", "/dashboard")


@frappe.whitelist(allow_guest=True)
def get_github_auth_url():
    success_uri = "http://newmktplace.localhost:8080/publishersetup"
    connected_app = get_connected_app()
    return connected_app.initiate_web_application_flow(success_uri=success_uri)


@frappe.whitelist()
def check_if_connected():
    connected_app = get_connected_app()
    return frappe.db.exists(
        "Token Cache",
        {
            "connected_app": connected_app.name,
            "user": frappe.session.user
        }
    )

# User Role Logic

def add_publisher_role_on_github_login(doc, method):
    role_name = "Marketplace Publisher"

    if not frappe.db.exists("Role", role_name):
        return

    if frappe.db.exists(
        "User Social Login",
        {
            "parent": doc.name,
            "provider": "github"
        }
    ):
        doc.add_roles(role_name)


# GitHub API

@frappe.whitelist()
def get_github_profile_data():
    headers = get_github_headers()
    res = requests.get("https://api.github.com/user", headers=headers)

    if res.status_code == 401:
        frappe.log_error(
            "GitHub 401: Invalid or expired token",
            "GitHub Integration"
        )
        return {"message": "Bad credentials", "status": "401"}

    return res.json()


@frappe.whitelist()
def get_publisher_repos():
    headers = get_github_headers()
    res = requests.get(
        "https://api.github.com/user/repos?type=owner&sort=updated",
        headers=headers
    )
    return res.json() if res.status_code == 200 else []

@frappe.whitelist()
def fetch_repo_info(repo_url):
    parts = repo_url.rstrip("/").split("/")
    owner, repo_name = parts[-2], parts[-1]
    headers = get_github_headers()

    repo_res = requests.get(f"https://api.github.com/repos/{owner}/{repo_name}", headers=headers)
    raw_github_data = repo_res.json() if repo_res.status_code == 200 else {}

    branches_res = requests.get(f"https://api.github.com/repos/{owner}/{repo_name}/branches", headers=headers)
    branches = [b["name"] for b in branches_res.json()] if branches_res.status_code == 200 else []

    app_folder = detect_app_folder(owner, repo_name, headers)
    hooks_content = fetch_hooks_content(owner, repo_name, app_folder, headers)
    metadata = extract_hooks_metadata(hooks_content, repo_name)

    return {
        "branches": branches,
        "default_branch": raw_github_data.get("default_branch", "main"),
        "metadata": metadata,
        "raw_github_data": raw_github_data
    }


def get_repo_and_branches(owner, repo_name, headers):
    repo_res = requests.get(
        f"https://api.github.com/repos/{owner}/{repo_name}",
        headers=headers
    )
    branches_res = requests.get(
        f"https://api.github.com/repos/{owner}/{repo_name}/branches",
        headers=headers
    )

    default_branch = "main"
    if repo_res.status_code == 200:
        default_branch = repo_res.json().get("default_branch", "main")

    branches = []
    if branches_res.status_code == 200:
        branches = [b["name"] for b in branches_res.json()]

    return default_branch, branches


def detect_app_folder(owner, repo_name, headers):
    tree_res = requests.get(
        f"https://api.github.com/repos/{owner}/{repo_name}/git/trees/HEAD?recursive=1",
        headers=headers
    )

    if tree_res.status_code != 200:
        return None

    for item in tree_res.json().get("tree", []):
        if item["path"].endswith("hooks.py"):
            return item["path"].split("/")[0]

    return None

def fetch_hooks_content(owner, repo_name, app_folder, headers):
    if not app_folder:
        return None

    res = requests.get(
        f"https://api.github.com/repos/{owner}/{repo_name}/contents/{app_folder}/hooks.py",
        headers=headers
    )

    if res.status_code != 200:
        return None

    return base64.b64decode(res.json()["content"]).decode("utf-8")


def extract_hooks_metadata(content, fallback_name):
    metadata = {
        "app_name": fallback_name,
        "app_title": fallback_name.replace("_", " ").title(),
        "app_description": "",
        "dependencies": []
    }

    if not content:
        return metadata

    def extract_var(name):
        match = re.search(rf"{name}\s*=\s*['\"](.*?)['\"]", content)
        return match.group(1) if match else None

    metadata["app_name"] = extract_var("app_name") or metadata["app_name"]
    metadata["app_title"] = extract_var("app_title") or metadata["app_title"]
    metadata["app_description"] = extract_var("app_description") or ""

    dep_match = re.search(r"required_apps\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if dep_match:
        metadata["dependencies"] = [
            a.strip().strip("'\"")
            for a in dep_match.group(1).split(",")
            if a.strip()
        ]

    return metadata
