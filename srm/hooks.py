# Copyright 2026 Rmli-sa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

# Core CRM window actions whose ``domain``/``context`` this module overrides
# in place (see ``views/crm_lead.xml``) so that the CRM app hides supplier
# records. Odoo's uninstall only deletes records *owned* by this module;
# these belong to ``crm`` and would otherwise keep a domain on a column that
# no longer exists, breaking the CRM app until ``crm`` is updated.
# The values below are the ``crm`` 19.0 definitions, restored on uninstall.
CORE_ACTIONS = {
    "crm.crm_lead_all_leads": {
        "domain": "['|', ('type','=','lead'), ('type','=',False)]",
        "context": (
            "{'default_type':'lead', 'search_default_type': 'lead', "
            "'search_default_to_process':1}"
        ),
    },
    "crm.crm_opportunity_report_action": {"domain": False},
    "crm.crm_opportunity_report_action_lead": {"domain": False},
}


def uninstall_hook(env):
    for xmlid, values in CORE_ACTIONS.items():
        action = env.ref(xmlid, raise_if_not_found=False)
        if action:
            action.write(values)
