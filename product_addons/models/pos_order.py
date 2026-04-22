from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    a_b_value = fields.Float(string='Average Bill Value', compute='_compute_a_b_value',compute_sudo=True, store=True, aggregator="avg")
    upt_value = fields.Float(string='Unit Per Transaction', compute='_compute_upt_value',compute_sudo=True, store=True, aggregator="avg")
    
    @api.depends('lines')
    def _compute_a_b_value(self):
        for move in self:
            total_amount = sum(line.price_subtotal_incl for line in move.lines)
            total_quantity = sum(line.qty for line in move.lines)
            move.a_b_value = total_amount / total_quantity if total_quantity > 0 else 0.0
            
    @api.depends('lines')
    def _compute_upt_value(self):
        for move in self:
            move.upt_value = sum(line.qty for line in move.lines) / len(move) if move else 0.0