{
    'name': 'Product Addons',
    'version': '1.0',
    'category': 'Products',
    'author': 'Sudarsanan P.R',
    'website': '',
    'summary': 'Custom fields for product templates',
    'depends': ['base', 'sale', 'stock', 'point_of_sale', 'l10n_in_pos'],
    'data': [
        "views/product_template.xml",
        "views/mz_barcode_layout_38x25.xml",
    ],

    'license': 'OPL-1',
    'application': False,
    'auto_install': False,
    'installable': True,
    'assets': {
        'point_of_sale._assets_pos': [
            'product_addons/static/src/**/*',
        ],
    },
}