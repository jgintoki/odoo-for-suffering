# __manifest__.py
{
    'name': 'Client Basic Parameters',
    'version': '1.6.12',
    'summary': 'Basic parameters for client management',
    'sequence': 10,
    'description': """
        This module extends the res.partner model to include basic client parameters such as name,
        gender, region, comuna, nationality, marital status, marital regime, and worker type.
    """,
    'category': 'Client Management',
    'depends': ['base'], 
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/amicar_activity_type_view.xml',
    ],
    'views': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    "author": "jjcmjavascript",
}