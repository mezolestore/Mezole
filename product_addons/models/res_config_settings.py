from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    app_password = fields.Char(string="App Password", config_parameter='mezole.pos_password')
