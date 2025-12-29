# Copyright (c) 2025, BWH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MarketplacePublisherProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		bank_account_holder_name: DF.Data | None
		bank_account_number: DF.Data | None
		contact_email: DF.Data | None
		display_name: DF.Data | None
		email_for_notifications: DF.Data | None
		gstin: DF.Data | None
		other_bank_details: DF.SmallText | None
		paypal_id: DF.Data | None
		preferred_payout_method: DF.Literal["Frappe Cloud Credits", "Bank Transfer", "PayPal"]
		team: DF.Link
		website: DF.Data | None
	# end: auto-generated types

	pass
