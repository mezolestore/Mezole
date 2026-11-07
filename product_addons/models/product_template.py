    # -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from collections import defaultdict
from odoo.tools import float_compare, float_is_zero


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    product_color = fields.Char(string='Product Color')
    product_size = fields.Char(string='Product Size')
    upc_code = fields.Char(string='UPC Code')
    mrp_price = fields.Float(string='MRP Price')
    is_upt_counted = fields.Boolean(string='Is UPT Counted')
    material_type_id = fields.Many2one('material.types', string='Material Type')
    
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
    material_type_id = fields.Many2one('material.types', string='Material Type')
    
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

    @api.depends('product_id', 'quantity')
    def _compute_total_value(self):
        for move in self:
            move.total_value = move.product_id.standard_price * move.quantity
            
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    total_value = fields.Float(string='Total Value', compute='_compute_total_value', store=True)
    total_quantity = fields.Float(string='Total Quantity', compute='_compute_total_value', store=True)

    @api.depends('move_ids.total_value')
    def _compute_total_value(self):
        for picking in self:
            if picking.move_ids:
                picking.total_quantity = sum(move.quantity for move in picking.move_ids)
                if picking.picking_type_code == 'incoming':
                    picking.total_value = sum(move.total_value for move in picking.move_ids)
                elif picking.picking_type_code == 'outgoing':
                    picking.total_value = -sum(move.total_value for move in picking.move_ids)
                    

class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()

        if 'zpl' in self.print_format:
            xml_id = 'stock.label_product_product'

        quantities = defaultdict(int)
        uom_unit = self.env.ref('uom.product_uom_categ_unit', raise_if_not_found=False)
        if self.move_quantity == 'move' and self.move_ids and all(float_is_zero(ml.quantity, precision_rounding=ml.product_uom_id.rounding) for ml in self.move_ids.move_line_ids):
            for move in self.move_ids:
                if move.product_uom.category_id == uom_unit:
                    use_reserved = float_compare(move.quantity, 0, precision_rounding=move.product_uom.rounding) > 0
                    useable_qty = move.quantity if use_reserved else move.product_uom_qty
                    if not float_is_zero(useable_qty, precision_rounding=move.product_uom.rounding):
                        quantities[move.product_id.id] += useable_qty
            data['quantity_by_product'] = {p: int(q) for p, q in quantities.items()}
        elif self.move_quantity == 'move' and self.move_ids.move_line_ids:
            custom_barcodes = defaultdict(list)
            for line in self.move_ids.move_line_ids:
                if line.product_uom_id.category_id == uom_unit:
                    if (line.lot_id or line.lot_name) and int(line.quantity):
                        custom_barcodes[line.product_id.id].append((line.lot_id.name or line.lot_name, int(line.quantity)))
                        continue
                    quantities[line.product_id.id] += line.quantity
                else:
                    quantities[line.product_id.id] = 1
            # Pass only products with some quantity done to the report
            data['quantity_by_product'] = {p: int(q) for p, q in quantities.items() if q}
            data['custom_barcodes'] = custom_barcodes
            if self.move_ids.picking_id.date_done:
                data['order_date_done'] = str(self.move_ids.picking_id.date_done.strftime('%B')[:3].upper() ) + str(self.move_ids.picking_id.date_done.year[:2])
            elif self.move_ids.picking_id.scheduled_date:
                data['order_date_done'] = str(self.move_ids.picking_id.scheduled_date.strftime('%B')[:3].upper() ) + str(self.move_ids.picking_id.scheduled_date.year[:2])
        return xml_id, data