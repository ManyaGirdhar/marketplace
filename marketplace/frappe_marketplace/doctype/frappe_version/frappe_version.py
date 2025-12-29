# Copyright (c) 2025, BWH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FrappeVersion(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from marketplace.frappe_marketplace.doctype.frappe_version_dependency.frappe_version_dependency import (
			FrappeVersionDependency,
		)

		default: DF.Check
		dependencies: DF.Table[FrappeVersionDependency]
		number: DF.Int
		public: DF.Check
		status: DF.Literal["Develop", "Beta", "Stable", "End of Life"]
	# end: auto-generated types

	pass
