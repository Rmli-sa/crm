# Copyright 2026 Rmli-sa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

# Core CRM records overridden in place by this module (``views/crm_lead.xml``)
# so that the CRM app hides supplier records, plus the records overridden by
# srm < 19.0.1.1.0. Odoo never resets a record owned by another module: on
# uninstall the crm-owned records would keep a domain on a column that no
# longer exists, and on upgrade the old pipeline override would keep filtering
# the CRM app on ``request_type = 'customer'``. The values below are the ``crm``
# 19.0 definitions.
CORE_RECORDS = {
    "crm.crm_lead_all_leads": {
        "domain": "['|', ('type','=','lead'), ('type','=',False)]",
        "context": (
            "{'default_type':'lead', 'search_default_type': 'lead', "
            "'search_default_to_process':1}"
        ),
    },
    "crm.crm_opportunity_report_action": {"domain": False},
    "crm.crm_opportunity_report_action_lead": {"domain": False},
    # overridden by srm < 19.0.1.1.0 only
    "crm.crm_lead_action_pipeline": {
        "domain": "[('type','=','opportunity')]",
        "context": (
            "{'default_type': 'opportunity', 'search_default_assigned_to_me': 1, "
            "'show_user_team_stages': 1}"
        ),
    },
    "crm.action_your_pipeline": {"code": "action = model.action_your_pipeline()"},
}
OVERRIDDEN_RECORDS = (
    "crm.crm_lead_all_leads",
    "crm.crm_opportunity_report_action",
    "crm.crm_opportunity_report_action_lead",
)
LEGACY_RECORDS = ("crm.crm_lead_action_pipeline", "crm.action_your_pipeline")


def restore_core_records(env, xmlids=None):
    """Write the core ``crm`` definition back on the given records."""
    for xmlid in xmlids or CORE_RECORDS:
        record = env.ref(xmlid, raise_if_not_found=False)
        if record:
            record.write(CORE_RECORDS[xmlid])


def uninstall_hook(env):
    restore_core_records(env)
