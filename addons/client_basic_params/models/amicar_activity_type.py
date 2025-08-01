from odoo import models, fields

class AmicarActivityType(models.Model):
    _name = 'amicar.activity.type'
    _description = 'Tipo de Actividad (catálogo)'

    name = fields.Char(string='Nombre', required=True)
    active = fields.Boolean(default=True)