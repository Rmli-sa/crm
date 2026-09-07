# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.fields import Domain
from odoo.tools.safe_eval import safe_eval


class Team(models.Model):
    _inherit = "crm.team"

    def _action_update_to_pipeline(self, action):
        """Split the shared pipeline between the CRM and SRM apps.

        Both ``action_your_pipeline`` ("My Pipeline") and
        ``action_opportunity_forecast`` ("Forecast") go through here, so the
        CRM menus need no core record edit. The SRM menus call the same methods
        with ``request_type='supplier'`` in the context and get supplier records
        only; the CRM app gets everything else, including records whose request
        type was never set (imports, incoming mails, website forms...).
        """
        action = super()._action_update_to_pipeline(action)
        if self.env.context.get("request_type") == "supplier":
            request_type_domain = Domain("request_type", "=", "supplier")
            action["context"]["default_request_type"] = "supplier"
        else:
            request_type_domain = Domain("request_type", "!=", "supplier")
            action["context"].setdefault("default_request_type", "customer")
        domain = action.get("domain") or []
        if isinstance(domain, str):
            domain = safe_eval(domain, {"uid": self.env.uid})
        action["domain"] = list(Domain.AND([Domain(domain), request_type_domain]))
        return action
