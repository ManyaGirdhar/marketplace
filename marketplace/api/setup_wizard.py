import hmac
from typing import Optional

import frappe
import requests
from frappe import _
from frappe.utils import get_url, md_to_html


@frappe.whitelist()
def initialize_app_step_1(form_data: str, repo_data=None):
	try:
		data = frappe.parse_json(form_data)
		if not repo_data:
			repo_data = data.get("repo_data") or {}
		elif isinstance(repo_data, str):
			repo_data = frappe.parse_json(repo_data)

		user = frappe.session.user

		frappe.log_error(
			title="Marketplace Debug: Repo Data Received",
			message=frappe.as_json({"data": data, "repo_data": repo_data}),
		)

		publisher = frappe.db.get_value("Marketplace Publisher", {"user": user}, "name")
		if not publisher:
			frappe.throw(_("Publisher profile not found. Please complete setup first."))

		app_title = data.get("app_title")
		if not app_title:
			frappe.throw(_("App Title is required."))

		if frappe.db.exists("Marketplace App", {"app": app_title}):
			frappe.throw(_("This app title '{0}' is already submitted to the Marketplace").format(app_title))

		return _process_app_initialization(data, repo_data, app_title, publisher)

	except Exception as e:
		frappe.log_error(title="Marketplace Error: initialize_app_step_1", message=frappe.get_traceback())
		raise e


def _process_app_initialization(data, repo_data, app_title, publisher):
	repo_full_url = data.get("repo_url") or repo_data.get("html_url")
	repo_owner = repo_data.get("owner", {}).get("login")
	repo_name = repo_data.get("name")

	if not frappe.db.exists("App", app_title):
		frappe.get_doc(
			{
				"doctype": "App",
				"title": app_title,
				"app_name": repo_name,
				"url": repo_full_url,
				"repo_owner": repo_owner,
				"repo": repo_name,
				"enabled": 1,
				"frappe": 1,
				"branch": repo_data.get("default_branch"),
				"publisher": publisher,
			}
		).insert(ignore_permissions=True)

	mkt_app = frappe.get_doc(
		{
			"doctype": "Marketplace App",
			"app": app_title,
			"title": app_title,
			"description": data.get("description") or repo_data.get("description"),
			"image": data.get("logo"),
			"status": "Draft",
			"publisher": publisher,
			"long_description": _("Fetching README from GitHub..."),
		}
	)

	last_release_name = None

	versions = data.get("versions", [])
	if not versions:
		frappe.throw(_("At least one version/branch must be selected."))

	for v in versions:
		version_num = v.get("version")
		selected_branch = v.get("branch")

		source_doc = frappe.get_doc(
			{
				"doctype": "App Source",
				"app": app_title,
				"repository_url": repo_full_url,
				"branch": selected_branch,
				"github_repo_full_name": repo_data.get("full_name") or f"{repo_owner}/{repo_name}",
				"public": 1,
			}
		).insert(ignore_permissions=True)

		release_doc = frappe.get_doc(
			{
				"doctype": "App Release",
				"app": app_title,
				"source": source_doc.name,
				"branch": selected_branch,
				"status": "Draft",
				"ci_status": "Running",
				"publisher": publisher,
			}
		).insert(ignore_permissions=True)

		last_release_name = release_doc.name

		mkt_app.append("sources", {"version": version_num, "source": source_doc.name})

		frappe.enqueue(
			"marketplace.api.setup_wizard.run_background_tasks",
			release_name=release_doc.name,
			source_name=source_doc.name,
			repo_full_name=repo_data.get("full_name") or f"{repo_owner}/{repo_name}",
			mkt_app_name=app_title,
			now=frappe.flags.in_test,
		)

	mkt_app.insert(ignore_permissions=True)

	return {"marketplace_app": mkt_app.name, "app_release": last_release_name}


def run_background_tasks(release_name, source_name, repo_full_name, mkt_app_name):
	release_doc = frappe.get_doc("App Release", release_name)
	source_doc = frappe.get_doc("App Source", source_name)

	dispatch_ci_validation(release_doc, repo_full_name)

	readme_html = fetch_readme_as_html(source_doc)
	if readme_html:
		frappe.db.set_value("Marketplace App", mkt_app_name, "long_description", readme_html)


def fetch_readme_as_html(source_doc):
	try:
		owner, repo = source_doc.repository_url.rstrip("/").split("/")[-2:]
		url = f"https://raw.githubusercontent.com/{owner}/{repo}/{source_doc.branch}/README.md"
		res = requests.get(url)
		if res.status_code == 200:
			return md_to_html(res.text)
	except Exception:
		pass
	return ""


def dispatch_ci_validation(release_doc, repo_full_name):
	secret_key = frappe.conf.get("marketplace_ci_secret")
	ci_repo = "frappe-community/marketplace"

	github_token = get_github_token(release_doc.owner)
	if not github_token:
		return

	url = f"https://api.github.com/repos/{ci_repo}/dispatches"
	payload = {
		"event_type": "validate_release",
		"client_payload": {
			"release_id": release_doc.name,
			"repo_full_name": repo_full_name,
			"branch": release_doc.branch,
			"app_name": release_doc.app,
			"secret_key": secret_key,
			"callback_url": f"{get_url()}/api/method/marketplace.api.setup_wizard.ci_callback",
		},
	}

	try:
		res = requests.post(
			url,
			json=payload,
			headers={
				"Authorization": f"token {github_token}",
				"Accept": "application/vnd.github.v3+json",
			},
			timeout=10,
		)
		if res.status_code != 204:
			frappe.log_error(f"CI Dispatch Failed ({res.status_code}): {res.text}", "Marketplace CI")
	except Exception as e:
		frappe.log_error(f"CI Connection Error: {e!s}", "Marketplace CI")


def get_github_token(user):
	connected_app_name = frappe.db.get_value("Connected App", {"provider_name": "Github"}, "name")
	if not connected_app_name:
		return None

	app = frappe.get_doc("Connected App", connected_app_name)
	token_cache = app.get_token_cache(user)
	return token_cache.get_password("access_token") if token_cache else None


@frappe.whitelist(allow_guest=True)  # nosemgrep
def ci_callback(release_id: str, status: str, secret_key: str, commit_hash: str | None = None):
	expected_secret = frappe.conf.get("marketplace_ci_secret")

	if not expected_secret or not hmac.compare_digest(str(secret_key), str(expected_secret)):
		frappe.throw(_("Unauthorized"), frappe.PermissionError)

	status_map = {"success": "Passed", "failure": "Failed", "cancelled": "Failed", "timed_out": "Failed"}

	frappe.db.set_value(
		"App Release",
		release_id,
		{"ci_status": status_map.get(status.lower(), "Running"), "hash": commit_hash},
		update_modified=True,
	)

	return {"status": "Updated"}


@frappe.whitelist()
def finalize_submission(app_release_id: str):
	release = frappe.get_doc("App Release", app_release_id)

	mkt_app_name = frappe.db.get_value("Marketplace App", {"app": release.app}, "name")

	if mkt_app_name:
		frappe.db.set_value("Marketplace App", mkt_app_name, "status", "Pending Review")

	return {"status": "success"}
