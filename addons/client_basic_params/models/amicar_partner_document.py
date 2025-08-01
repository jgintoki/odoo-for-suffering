from odoo import models, fields

class AmicarPartnerDocument(models.Model):
    _name = 'amicar.partner.document'
    _description = 'Amicar Partner Documents'

    name = fields.Char(string='Document Name', required=False)
    url = fields.Char(string='Document URL', required=False)
    download_uuid = fields.Char(string='Download UUID', required=False)
    document_type= fields.Char(string='Document Type', required=False)

    created_by_name = fields.Char(string='Created By Name', required=False)
    created_by_vat = fields.Char(string='Created By VAT', required=False)
    created_by_at = fields.Char(string='Created By AT', required=False)

    created_at = fields.Datetime(string='Created At', required=False)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
