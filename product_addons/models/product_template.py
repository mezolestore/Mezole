from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    product_color = fields.Char(string='Product Color')
    product_size = fields.Char(string='Product Size')
    upc_code = fields.Char(string='UPC Code')