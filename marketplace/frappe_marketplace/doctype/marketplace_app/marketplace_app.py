# Copyright (c) 2025, BWH and contributors
# For license information, please see license.txt

# import frappe
from frappe.website.website_generator import WebsiteGenerator


class MarketplaceApp(WebsiteGenerator):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from marketplace.frappe_marketplace.doctype.marketplace_app_categories.marketplace_app_categories import (
			MarketplaceAppCategories,
		)
		from marketplace.frappe_marketplace.doctype.marketplace_app_screenshot.marketplace_app_screenshot import (
			MarketplaceAppScreenshot,
		)
		from marketplace.frappe_marketplace.doctype.marketplace_app_version.marketplace_app_version import (
			MarketplaceAppVersion,
		)
		from marketplace.frappe_marketplace.doctype.marketplace_localisation_app.marketplace_localisation_app import (
			MarketplaceLocalisationApp,
		)

		after_install_script: DF.Code | None
		after_uninstall_script: DF.Code | None
		app: DF.Link
		average_rating: DF.Float
		categories: DF.Table[MarketplaceAppCategories]
		collect_feedback: DF.Check
		custom_verify_template: DF.Check
		description: DF.SmallText
		documentation: DF.Data | None
		frappe_approved: DF.Check
		image: DF.AttachImage | None
		localisation_apps: DF.Table[MarketplaceLocalisationApp]
		long_description: DF.TextEditor | None
		message: DF.TextEditor | None
		outgoing_email: DF.Data | None
		outgoing_sender_name: DF.Data | None
		poll_method: DF.Data | None
		privacy_policy: DF.Data | None
		published: DF.Check
		published_on: DF.Date | None
		review_stage: DF.Literal[
			"Not Started",
			"Description Missing",
			"Logo Missing",
			"App Release Not Reviewed",
			"Ready for Review",
			"Ready to Publish",
			"Rejected",
		]
		route: DF.Data | None
		run_after_install_script: DF.Check
		run_after_uninstall_script: DF.Check
		screenshots: DF.Table[MarketplaceAppScreenshot]
		show_for_site_creation: DF.Check
		signature: DF.TextEditor | None
		site_config: DF.JSON | None
		sources: DF.Table[MarketplaceAppVersion]
		status: DF.Literal["Draft", "Published", "In Review", "Attention Required", "Rejected", "Disabled"]
		stop_auto_review: DF.Check
		subject: DF.Data | None
		subscription_type: DF.Literal["Free", "Paid", "Freemium"]
		subscription_update_hook: DF.Data | None
		support: DF.Data | None
		team: DF.Link | None
		terms_of_service: DF.Data | None
		title: DF.Data
		website: DF.Data | None
	# end: auto-generated types

	pass
