from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    tax_slab_ids = fields.One2many('tax.slab', 'company_rel' , string="Tax Slab")

class TaxSlab(models.Model):
    _name = 'tax.slab'

    category_id = fields.Many2one('product.category' , string="Category")
    price_from = fields.Float(string="Price From")
    price_to = fields.Float(string="Price To")
    tax_id = fields.Many2many('account.tax' ,string="Tax")
    company_rel = fields.Many2one('res.company' , string="Company")
    is_sale = fields.Boolean(string="Sale")
    is_purchase= fields.Boolean(string="Purchase")