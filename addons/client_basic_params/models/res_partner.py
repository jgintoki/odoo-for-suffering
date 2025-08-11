# addons/tu_modulo/models/res_partner.py
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # -- Campos originales de res.partner
    mobile = fields.Char(
        string='Celular',
        tracking=True,        
        help='Teléfono celular del contacto'
    )

    # -- Campos personalizados para el cliente
    first_name = fields.Char(string='Nombre', required=True, tracking=True, help='Nombre del cliente')
    last_name_father = fields.Char(string='Apellido paterno', tracking=True, help='Apellido paterno del cliente')
    last_name_mother = fields.Char(string='Apellido materno', tracking=True, help='Apellido materno del cliente')

    # -- Antecedentes del Cliente
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro'),
    ], string='Sexo', tracking=True)


    birthdate_date = fields.Date(string='Fecha de Nacimiento', tracking=True)

    nationality_id = fields.Many2one(
        'res.country', string='Nacionalidad', tracking=True)

    marital_status = fields.Selection([
        ('single', 'Soltero(a)'),
        ('married', 'Casado(a)'),
        ('divorced', 'Divorciado(a)'),
        ('widowed', 'Viudo(a)'),
    ], string='Estado Civil', tracking=True)

    marital_regime = fields.Selection([
        ('sep_assets', 'Separación de bienes'),
        ('community_property', 'En comunidad de bienes'),
        ('participation_gains', 'Participación de ganancias'),
    ], string='Reg. Matrimonial', tracking=True)

    # -- Antecedentes de Actividad
    worker_type = fields.Selection([
        ('dependent', 'Dependiente'),
        ('independent', 'Independiente'),
    ], string='Tipo de Trabajador', tracking=True)

    amicar_activity_type_id = fields.Many2one(
        'amicar.activity.type',
        string='Tipo de Actividad Amicar', tracking=True
    )

    employment_date = fields.Date(string='Fecha de Ingreso', tracking=True)

    document_ids = fields.One2many(
        'amicar.partner.document',
        'partner_id',
        string='Documentos',
        help='Documentos asociados al cliente',
        tracking=True,
    )

    document_links = fields.Html(
        string='Documentos',
        compute='_compute_document_links',
        sanitize=False,
        readonly=True,
        help='Lista de documentos asociados al cliente, con enlaces para descargar.',
        tracking=True,
    )
    
    latest_document_ids = fields.Many2many(
        comodel_name='amicar.partner.document',
        compute='_compute_latest_documents',
        string='Documentos recientes (1 por tipo)',
        store=False,
        help='Lista de documentos más recientes por tipo, para mostrar en vistas.',
        tracking=True,
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

    # -----------------------------------------------------------------------
    # Helper que normaliza cualquier fecha a objeto datetime
    # -----------------------------------------------------------------------
    @staticmethod
    def _to_datetime(value):
        if not value:
                return fields.Datetime.now()
        if isinstance(value, fields.Datetime):
            return value
        # Aceptar formato ISO con 'T'
        return fields.Datetime.from_string(value.replace('T', ' '))

    # -----------------------------------------------------------------------
    # Cálculo del listado único por tipo, más reciente
    # -----------------------------------------------------------------------
    @api.depends('document_ids', 'document_ids.created_by_at', 'document_ids.created_at')
    def _compute_latest_documents(self):
        for partner in self:
            latest_by_type = {}
            for doc in partner.document_ids:
                dtype = doc.document_type or _('Sin tipo')
                doc_date = self._to_datetime(doc.created_by_at or doc.created_at)
                # mantén sólo el más nuevo por tipo
                if (dtype not in latest_by_type) or (doc_date > latest_by_type[dtype][1]):
                    latest_by_type[dtype] = (doc, doc_date)

            partner.latest_document_ids = partner.env['amicar.partner.document'].browse(
                [tpl[0].id for tpl in latest_by_type.values()]
            )

    # -----------------------------------------------------------------------
    # links HTML (ya depurado para lista <ul><li>)
    # -----------------------------------------------------------------------
    @api.depends('latest_document_ids')
    def _compute_document_links(self):
        for partner in self:
            lis = []
            for idx, doc in enumerate(partner.latest_document_ids, 1):
                label = doc.document_type or doc.name or _('Documento')
                href = doc.url or (f"/download/{doc.download_uuid}" if doc.download_uuid else "#")
                lis.append(f'<li><a href="{href}" target="_blank">{idx} - {label}</a></li>')
            partner.document_links = f"<ul>{''.join(lis)}</ul>" if lis else False

            latest_by_type = {}

            # 1⃣  Ordena por fecha DESC
            docs_sorted = sorted(
                partner.document_ids,
                key=lambda d: self._to_datetime(d.created_by_at or d.created_at),
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