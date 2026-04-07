from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    product_color = fields.Char(string='Product Color')
    product_size = fields.Char(string='Product Size')
    upc_code = fields.Char(string='UPC Code')
    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    
    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if not val.get('barcode'):
                val['barcode'] = self.env['ir.sequence'].next_by_code('product.barcode')
        return super(ProductProduct, self).create(vals_list)