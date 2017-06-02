# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytz
from datetime import datetime
from odoo import models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def get_printscreen_report_context(self):
        tz = pytz.timezone(self.tz) if self.tz else pytz.utc
        date = datetime.now(tz)

        lang = self.env['res.lang'].search(
            [('code', '=', self.lang or 'en_US')], limit=1)

        current_date = date.strftime(lang.date_format)

        return {
            'company_name': self.company_id.name,
            'company_logo': self.company_id.logo,
            'current_date': current_date,
        }
