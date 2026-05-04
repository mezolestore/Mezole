from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    abvalue = fields.Float(string='Average Bill Value', compute='_compute_a_b_value', compute_sudo=True, store=True, aggregator="avg")
    upt_value = fields.Float(string='Unit Per Transaction', compute='_compute_upt_value', compute_sudo=True, store=True, aggregator="avg")
    
    @api.depends('lines.price_subtotal_incl')
    def _compute_a_b_value(self):
        for move in self:
            move.abvalue = sum(move.lines.mapped('price_subtotal_incl'))

    @api.depends('lines')
    def _compute_upt_value(self):
        for move in self:
            move.upt_value = sum(line.qty for line in move.lines) / len(move) if move else 0.0