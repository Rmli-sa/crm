# Copyright 2026 Rmli-sa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID, api

from odoo.addons.srm.hooks import LEGACY_RECORDS, restore_core_records


def migrate(cr, version):
    """Reset the core pipeline records overridden in place by srm < 19.0.1.1.0.

    Those overrides are no longer declared by the module, so a plain upgrade
    would leave the CRM pipeline filtered on ``request_type = 'customer'``.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    restore_core_records(env, LEGACY_RECORDS)
