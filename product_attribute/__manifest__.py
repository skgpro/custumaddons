# -*- encoding: utf-8 -*-

{
    'name': 'Product Custom Attribute',
    'version': '1.0',
    'category': 'Product',
    'author': 'Prolitus Technologies Pvt. Ltd.',
    'sequence': 50,
    'summary': 'Product Attribute',
    'depends': ['web', 'base', 'product', 'sale'],
    'website': 'www.prolitus.com',
    'description': """
         This module helps to manage product custom attributes.
    """,
    'data': [
            'security/ir.model.access.csv',
            'views/product_attribute_view.xml',
    ],
    'qweb': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
