# -*- coding: utf-8 -*-

{
    'name': 'Mezole Report Customization',
    'version': '18.0.0.1',
    'website': '',
    'license': "LGPL-3",
    'depends': ['sale', 'report_xlsx', 'stock', 'point_of_sale'],
    'maintainer': '',
    'support': '',
    'description': 
        """ 
        This module allows customizations for gst report.
        """,
     'images': [],
    'data': [
        'security/ir.model.access.csv',              # ✅ Access rights (needs models loaded via __init__)
        'reports/report.xml',                         # ✅ Reports (safe here)
        'wizard/gst_report_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mezole_gst_report_customization/static/src/js/xlsx_report_download_patch.js',
        ],
    },

    'test': [],
    'installable': True,
    'auto_install': False,
    'category': '',
}

