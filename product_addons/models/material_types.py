from odoo import models, fields, api

class MaterialTypes(models.Model):
    _name = "material.types"
    _description = "Material Types"

    name = fields.Char(string="Material Type", required=True)
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)