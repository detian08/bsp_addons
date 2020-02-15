{
    "name"          : "Purchase Report",
    "version"       : "1.0",
    "author"        : "IT Dept Bina San Prima",
    "website"       : "https://www.binasanprima.com/",
    "category"      : "Purchases",
    "summary"       : "Purchase Report in Excel Format",
    "description"   : """
        
    """,
    "depends"       : [
        "base",
        "purchase",
        "bsp_cosmetics",
        "purchase_order_type",
        "aos_partner_taxes",
        "purchase_request_recap_dk_xlsx",
        "purchase_request_recap_qcf",
    ],
    "data"          : [
        "wizard/bsp_purchase_report_wizard.xml",
    ],
    "demo"          : [],
    "test"          : [],
    "images"        : [],
    "qweb"          : [],
    "css"           : [],
    "application"   : True,
    "installable"   : True,
    "auto_install"  : False,
}