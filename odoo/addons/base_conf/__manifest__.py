{
    "name" : "base_conf",
    'version': '1.0',
    "author" : "Linktic",
    "category" : "Base",
    "description" : """Módulo base, con funciones genericas usadas por los otros modulos. """,
    "depends" : [
        'base',
        'mail',
    ],
    "data" : [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/base_view.xml',
        'views/res_city_view.xml',
        'views/config_firma_ws_view.xml',
        'wizard/registrar_mensaje_view.xml',
        # 'wizard/registrar_direccion_view.xml',
        # 'wizard/mensaje_ejecutar_codigo_view.xml',
    ],
    "test": [
    ],
    "installable" : True,
    "external_dependencies": {
        "python": [
            'appy'
        ],
    },
    "license":"LGPL-3"
}