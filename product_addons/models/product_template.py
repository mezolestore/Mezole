from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    product_color = fields.Char(string='Product Color')
    product_size = fields.Char(string='Product Size')
    upc_code = fields.Char(string='UPC Code')
    mrp_price = fields.Float(string='MRP Price')
    is_upt_counted = fields.Boolean(string='Is UPT Counted')
    
    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if not val.get('barcode'):
                val['barcode'] = self.env['ir.sequence'].next_by_code('product.barcode')
        return super(ProductTemplate, self).create(vals_list)
    
    @api.model
    def _load_pos_data_fields(self, config_id):
        result = super()._load_pos_data_fields(config_id)
        result += ['qty_available']
        return result

    
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
    
    @api.model
    def _load_pos_data_fields(self, config_id):
        result = super()._load_pos_data_fields(config_id)
        result += ['qty_available']
        return result
    
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    city_area_id = fields.Many2one('city.area', string='City Area')
    how_know_us = fields.Selection([
        ('walk_in', 'Walk-in'),
        ('nearby', 'Nearby Resident'),
        ('google', 'Google Search'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('friend', 'Friend/Referral'),
        ('existing_customer', 'Existing Customer'),
        ('hoarding', 'Hoarding/Banner'),
        ('newspaper', 'Newspaper/Magazine'),
        ('event', 'Event/Promotion'),
        ('other', 'Other'),
    ], string='How did you hear about us?')
    
class StockMove(models.Model):
    _inherit = 'stock.move'
    
    total_value = fields.Float(string='Total Value', compute='_compute_total_value', store=True)

    def _compute_total_value(self):
        for move in self:
            move.total_value = move.product_id.standard_price * move.quantity
            
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    total_value = fields.Float(string='Total Value', compute='_compute_total_value')

    def _compute_total_value(self):
        for picking in self:
            if picking.move_ids:
                if picking.picking_type_code == 'incoming':
                    picking.total_value = sum(move.total_value for move in picking.move_ids)
                elif picking.picking_type_code == 'outgoing':
                    picking.total_value = -sum(move.total_value for move in picking.move_ids)