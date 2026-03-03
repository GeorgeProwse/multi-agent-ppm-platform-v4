"""
Vendor & Procurement Management Agent - Action Handlers

Each sub-module contains one or more action handler functions extracted from
the monolithic VendorProcurementAgent class.
"""

from actions.contract import handle_create_contract, handle_sign_contract
from actions.invoice import handle_reconcile_invoice, handle_submit_invoice
from actions.onboard_vendor import handle_onboard_vendor
from actions.procurement_request import handle_create_procurement_request
from actions.purchase_order import handle_create_purchase_order
from actions.research_vendor import handle_research_vendor
from actions.rfp import (
    handle_evaluate_proposals,
    handle_generate_rfp,
    handle_select_vendor,
    handle_submit_proposal,
)
from actions.vendor_performance import (
    handle_get_vendor_scorecard,
    handle_track_vendor_performance,
)
from actions.vendor_profile import (
    handle_get_vendor_profile,
    handle_list_vendor_profiles,
    handle_update_vendor_profile,
)
from actions.vendor_search import handle_get_procurement_status, handle_search_vendors

__all__ = [
    "handle_create_contract",
    "handle_create_procurement_request",
    "handle_create_purchase_order",
    "handle_evaluate_proposals",
    "handle_generate_rfp",
    "handle_get_procurement_status",
    "handle_get_vendor_profile",
    "handle_get_vendor_scorecard",
    "handle_list_vendor_profiles",
    "handle_onboard_vendor",
    "handle_reconcile_invoice",
    "handle_research_vendor",
    "handle_search_vendors",
    "handle_select_vendor",
    "handle_sign_contract",
    "handle_submit_invoice",
    "handle_submit_proposal",
    "handle_track_vendor_performance",
    "handle_update_vendor_profile",
]
