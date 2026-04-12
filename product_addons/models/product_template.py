from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    product_color = fields.Char(string='Product Color')
    product_size = fields.Char(string='Product Size')
    upc_code = fields.Char(string='UPC Code')
    mrp_price = fields.Float(string='MRP Price')
    
    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if not val.get('barcode'):
                val['barcode'] = self.env['ir.sequence'].next_by_code('product.barcode')
        return super(ProductTemplate, self).create(vals_list)

    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    mrp_price = fields.Float(string='MRP Price', related='product_tmpl_id.mrp_price', store=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if val.get('product_tmpl_id'):
                template = self.env['product.template'].browse(val['product_tmpl_id'])
                if template.barcode:
                    val['barcode'] = template.barcode
            if not val.get('barcode'):
                val['barcode'] = self.env['ir.sequence'].next_by_code('product.barcode')
        return super(ProductProduct, self).create(vals_list)