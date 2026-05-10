from datetime import date
from odoo import fields, models, api
from odoo.exceptions import UserError


class GSTReport(models.TransientModel):
    _name = 'gst.filing.report.wiz'
    _description = 'GST Report Wizard'


    from_date = fields.Date(string="From Date" , required=True)
    to_date = fields.Date(string="To Date", required=True)
    types = fields.Selection([('invoice','Invoice'),
                                 ('hsn','HSN')], string="Type", required=True)
    
    def action_print_report(self):
        for rec in self:
            if rec.from_date > rec.to_date:
                raise UserError("'To Date' is lesser than 'From Date'.Please check the date")
            else:
                action = self.env.ref('mezole_gst_report_customization.gst_filing_report_xlsx').with_context(self.env.context).report_action(self, data={
                    'from_date': self.from_date.isoformat(),
                    'to_date': self.to_date.isoformat(),
                    'types': self.types,
                })
                return action