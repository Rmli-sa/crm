# Copyright 2026 Rmli-sa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.fields import Domain
from odoo.tests.common import TransactionCase, tagged
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.addons.srm.hooks import CORE_ACTIONS, uninstall_hook


@tagged("lead_manage")
class TestSrmVisibility(TransactionCase):
    """SRM shows only supplier records; CRM shows everything else."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        Lead = cls.env["crm.lead"]
        cls.customer_opp = Lead.create(
            {"name": "Customer opp", "type": "opportunity", "request_type": "customer"}
        )
        cls.supplier_opp = Lead.create(
            {"name": "Supplier opp", "type": "opportunity", "request_type": "supplier"}
        )
        cls.unset_opp = Lead.create({"name": "Unset opp", "type": "opportunity"})
        cls.customer_lead = Lead.create(
            {"name": "Customer lead", "type": "lead", "request_type": "customer"}
        )
        cls.supplier_lead = Lead.create(
            {"name": "Supplier lead", "type": "lead", "request_type": "supplier"}
        )
        cls.unset_lead = Lead.create({"name": "Unset lead", "type": "lead"})
        cls.all_records = (
            cls.customer_opp
            | cls.supplier_opp
            | cls.unset_opp
            | cls.customer_lead
            | cls.supplier_lead
            | cls.unset_lead
        )

    def _records_of(self, action):
        """Records of the fixture matched by an action's domain."""
        domain = action["domain"] or []
        if isinstance(domain, str):
            domain = safe_eval(domain, {"uid": self.env.uid})
        return self.env["crm.lead"].search(
            Domain.AND([Domain(domain), Domain("id", "in", self.all_records.ids)])
        )

    def _action(self, xmlid):
        return self.env["ir.actions.actions"]._for_xml_id(xmlid)

    def test_crm_pipeline_hides_supplier_only(self):
        action = self.env["crm.team"].action_your_pipeline()
        self.assertEqual(self._records_of(action), self.customer_opp | self.unset_opp)
        self.assertEqual(action["context"]["default_request_type"], "customer")

    def test_srm_pipeline_shows_supplier_only(self):
        action = (
            self.env["crm.team"]
            .with_context(request_type="supplier")
            .action_your_pipeline()
        )
        self.assertEqual(self._records_of(action), self.supplier_opp)
        self.assertEqual(action["context"]["default_request_type"], "supplier")

    def test_forecast_is_split_the_same_way(self):
        Team = self.env["crm.team"]
        self.assertEqual(
            self._records_of(Team.action_opportunity_forecast()),
            self.customer_opp | self.unset_opp,
        )
        self.assertEqual(
            self._records_of(
                Team.with_context(request_type="supplier").action_opportunity_forecast()
            ),
            self.supplier_opp,
        )

    def test_leads_menus(self):
        self.assertEqual(
            self._records_of(self._action("crm.crm_lead_all_leads")),
            self.customer_lead | self.unset_lead,
        )
        self.assertEqual(
            self._records_of(self._action("srm.srm_lead_all_leads")),
            self.supplier_lead,
        )

    def test_reporting_menus(self):
        non_supplier = self.all_records - self.supplier_opp - self.supplier_lead
        for xmlid in (
            "crm.crm_opportunity_report_action",
            "crm.crm_opportunity_report_action_lead",
        ):
            self.assertEqual(self._records_of(self._action(xmlid)), non_supplier, xmlid)
        self.assertEqual(
            self._records_of(self._action("srm.srm_opportunity_action_dashboard")),
            self.supplier_opp | self.supplier_lead,
        )

    def test_manual_switch_moves_record_between_apps(self):
        Team = self.env["crm.team"]
        srm = Team.with_context(request_type="supplier")
        self.unset_opp.request_type = "supplier"
        self.assertEqual(
            self._records_of(srm.action_your_pipeline()),
            self.supplier_opp | self.unset_opp,
        )
        self.assertEqual(
            self._records_of(Team.action_your_pipeline()), self.customer_opp
        )

        self.supplier_opp.request_type = False
        self.assertEqual(self._records_of(srm.action_your_pipeline()), self.unset_opp)
        self.assertEqual(
            self._records_of(Team.action_your_pipeline()),
            self.customer_opp | self.supplier_opp,
        )

    def test_uninstall_hook_restores_core_actions(self):
        for xmlid in CORE_ACTIONS:
            self.assertIn("request_type", self.env.ref(xmlid).domain, xmlid)
        uninstall_hook(self.env)
        for xmlid, values in CORE_ACTIONS.items():
            action = self.env.ref(xmlid)
            for field, value in values.items():
                self.assertEqual(action[field], value, f"{xmlid}.{field}")
            self.assertNotIn("request_type", action.domain or "", xmlid)
