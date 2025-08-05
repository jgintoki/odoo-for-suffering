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
        Muestra **máx. 1 documento por tipo**, tomando el más reciente
        (created_by_at || created_at).  Renderiza como <ul><li>…</li></ul>
        """
        # Helper para convertir la fecha (str o datetime) a objeto datetime
        def _to_dt(value):
            if not value:
                return fields.Datetime.now()
            if isinstance(value, fields.Datetime):
                return value
            # value viene como str ISO-8601 ('2023-10-01T12:00:00')
            value = value.replace('T', ' ')
            return fields.Datetime.from_string(value)

        for partner in self:
            latest_by_type = {}

            # 1⃣  Ordena por fecha DESC
            docs_sorted = sorted(
                partner.document_ids,
                key=lambda d: _to_dt(d.created_by_at or d.created_at),
                reverse=True,
            )

            # 2⃣  Guarda sólo el primero de cada tipo
            for doc in docs_sorted:
                doc_type = doc.document_type or _('Sin tipo')
                if doc_type not in latest_by_type:
                    latest_by_type[doc_type] = doc

            # 3⃣  Renderiza <ul><li>…</li></ul>
            items = []
            for idx, (doc_type, doc) in enumerate(latest_by_type.items(), start=1):
                href = doc.url or (f"/download/{doc.download_uuid}"
                                   if doc.download_uuid else "#")
                label = f"{idx} - {doc_type}"
                items.append(f'<li><a href="{href}" target="_blank">{label}</a></li>')

            partner.document_links = (
                f"<ul>{''.join(items)}</ul>" if items else False
            )