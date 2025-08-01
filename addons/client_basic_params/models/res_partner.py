# addons/tu_modulo/models/res_partner.py
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    first_name = fields.Char(string='Nombre', required=True)
    last_name_father = fields.Char(string='Apellido paterno')
    last_name_mother = fields.Char(string='Apellido materno')

    # -- Antecedentes del Cliente
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro'),
    ], string='Sexo')

    birthdate_date = fields.Date(string='Fecha de Nacimiento')
    
    nationality_id = fields.Many2one(
        'res.country', string='Nacionalidad')

    marital_status = fields.Selection([
        ('single', 'Soltero(a)'),
        ('married', 'Casado(a)'),
        ('divorced', 'Divorciado(a)'),
        ('widowed', 'Viudo(a)'),
    ], string='Estado Civil')

    marital_regime = fields.Selection([
        ('sep_assets', 'Separación de bienes'),
        ('community_property', 'En comunidad de bienes'),
        ('participation_gains', 'Participación de ganancias'),
    ], string='Reg. Matrimonial')

    # -- Antecedentes de Actividad
    worker_type = fields.Selection([
        ('dependent', 'Dependiente'),
        ('independent', 'Independiente'),
    ], string='Tipo de Trabajador')

    amicar_activity_type_id = fields.Many2one(
        'amicar.activity.type',
        string='Tipo de Actividad Amicar'
    )

    employment_date = fields.Date(string='Fecha de Ingreso')

    document_ids = fields.One2many(
        'amicar.partner.document',
        'partner_id',
        string='Documentos',
    )

    document_links = fields.Html(
        string='Documentos',
        compute='_compute_document_links',
        sanitize=False,
        readonly=True,
    )
    
    # Mantener «name» (el nombre completo) sincronizado
    @api.onchange('first_name', 'last_name_father', 'last_name_mother')
    def _onchange_split_name(self):
        for rec in self:
            parts = [rec.first_name, rec.last_name_father, rec.last_name_mother]
            rec.name = " ".join(p for p in parts if p).strip()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = " ".join(
                p for p in [
                    vals.get('first_name'),
                    vals.get('last_name_father'),
                    vals.get('last_name_mother'),
                ] if p
            ).strip()
        return super().create(vals_list)

    def write(self, vals):
        # Si llegan campos separados, recalculamos «name»
        if {'first_name', 'last_name_father', 'last_name_mother'} & vals.keys():
            for rec in self:
                data = {
                    'first_name': vals.get('first_name', rec.first_name),
                    'last_name_father': vals.get('last_name_father', rec.last_name_father),
                    'last_name_mother': vals.get('last_name_mother', rec.last_name_mother),
                }
                vals.setdefault('name', " ".join(p for p in data.values() if p).strip())
        return super().write(vals)

    # Opcional: para que las búsquedas por cualquiera de las partes funcionen
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = ['|', '|',
                  ('first_name', operator, name),
                  ('last_name_father', operator, name),
                  ('last_name_mother', operator, name)]
        return super()._name_search(name, args + domain, operator, limit, name_get_uid=name_get_uid)

    @api.depends('document_ids')
    def _compute_document_links(self):
        """
        Renderiza algo como:
        <a href="http://.../file1.pdf" target="_blank" class="badge badge-primary me-1">
            1 - Contrato
        </a>
        """
        for partner in self:
            tags = []
            for idx, doc in enumerate(partner.document_ids, start=1):
                # ► Etiqueta a mostrar
                label = doc.document_type or doc.name or _('Documento')

                # ► URL a la que apunta
                href = (
                    doc.url
                    or (f"/download/{doc.download_uuid}" if doc.download_uuid else "#")
                )

                # ► Construir el tag
                tags.append(
                    f'<a href="{href}" target="_blank" '
                    f'class="badge badge-primary me-1">{idx} - {label}</a>'
                )

            partner.document_links = (
                "<div>" + " ".join(tags) + "</div>" if tags else False
            )