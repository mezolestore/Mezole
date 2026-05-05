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
            
            
class PosSession(models.Model):
    _inherit = 'pos.session'
            
            
    def find_product_by_barcode(self, barcode, config_id):
        product_fields = self.env['product.product']._load_pos_data_fields(config_id)
        template_fields = self.env['product.template']._load_pos_data_fields(config_id)
        product_packaging_fields = self.env['product.packaging']._load_pos_data_fields(config_id)
        product_context = {**self.env.context, 'display_default_code': False}
        product = self.env['product.product'].search([
            ('barcode', '=', barcode),
            ('sale_ok', '=', True),
            ('available_in_pos', '=', True),
        ])
        if product and product[0].barcode == barcode:
            return {'product.product': product.with_context(product_context).read(product_fields, load=False)}
        # If not found, search in product.template
        product_template = self.env['product.template'].search([
            ('barcode', '=', barcode),
            ('sale_ok', '=', True),
            ('available_in_pos', '=', True),
        ])
        if product_template and product_template[0].barcode == barcode:
            return {'product.template': product_template.with_context(product_context).read(template_fields, load=False)}

        domain = [('barcode', 'not in', ['', False])]
        loaded_data = self._context.get('loaded_data')
        if loaded_data:
            loaded_product_ids = [x['id'] for x in loaded_data['product.product']]
            domain = AND([domain, [('product_id', 'in', [x['id'] for x in self._context.get('loaded_data')['product.product']])]]) if self._context.get('loaded_data') else []
            domain = AND([domain, [('product_id', 'in', loaded_product_ids)]])
        packaging_params = {
            'search_params': {
                'domain': domain,
                'fields': ['name', 'barcode', 'product_id', 'qty'],
            },
        }
        packaging_params['search_params']['domain'] = [['barcode', '=', barcode]]
        packaging = self.env['product.packaging'].search(packaging_params['search_params']['domain'])

        if packaging and packaging.product_id:
            return {'product.product': packaging.product_id.with_context(product_context).read(product_fields, load=False), 'product.packaging': packaging.read(product_packaging_fields, load=False)}
        else:
            return {
                'product.product': [],
                'product.packaging': [],
            }