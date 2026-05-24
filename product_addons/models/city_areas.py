from odoo import models, fields

class CityArea(models.Model):
    _name = 'city.area'
    _description = 'City Area'

    name = fields.Char(string='Area Name', required=True)
    city_id = fields.Many2one('res.city', string='City')