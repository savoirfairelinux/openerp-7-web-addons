# -*- coding: utf-8 -*-
# © 2013 ZestyBeanz Technologies Pvt. Ltd.
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Web Printscreen ZB',
    'version': '1.4',
    'category': 'Web',
    'description': """
        Module to export current active tree view in to excel report
    """,
    'author': 'Zesty Beanz Technologies',
    'website': 'http://www.zbeanztech.com',
    'depends': ['web'],
    'data': [
        'views/web_printscreen_zb.xml',
    ],
    'qweb': [
        'static/src/xml/web_printscreen_export.xml',
    ],
    'installable': True,
    'auto_install': False,
    'web_preload': False,
}
