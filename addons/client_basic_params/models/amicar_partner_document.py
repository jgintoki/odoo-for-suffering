from odoo import models, fields

class AmicarPartnerDocument(models.Model):
    _name = 'amicar.partner.document'
    _description = 'Amicar Partner Documents'

    name = fields.Char(string='Nombre', required=False)
    url = fields.Char(string='URL del Documento', required=False)
    download_uuid = fields.Char(string='UUID de Descarga', required=False, tracking=True)
    document_type = fields.Char(string='Tipo de Documento', required=False, tracking=True)
    source = fields.Char(string='Fuente del Documento', required=False, tracking=True)
    signed = fields.Boolean(string='Firmado', default=False, required=False, tracking=True)
    status = fields.Selection([
        ('CREATED', 'Creado'),
        ('SIGNING', 'Firmando'),
        ('ERROR', 'Error'),
        ('SIGNED', 'Firmado'),
        ('REJECTED', 'Rechazado'),
        ('CANCELLED', 'Cancelado')
    ], string='Estado del Documento', required=False, tracking=True)

    created_by_name = fields.Char(string='Nombre del Creador', required=False, tracking=True)
    created_by_vat = fields.Char(string='VAT del Creador', required=False, tracking=True)
    created_by_at = fields.Char(string='AT del Creador', required=False, tracking=True)

    created_at = fields.Datetime(string='Fecha de Creación', required=False)
    partner_id = fields.Many2one('res.partner', string='Socio', required=True, tracking=True)
