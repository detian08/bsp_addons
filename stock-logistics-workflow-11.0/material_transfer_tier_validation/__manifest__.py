{
    "name": "Material Transfer Tier Validation",
    "summary": "Extends the functionality of Material Transfer to "
               "support a tier validation process.",
    "version": "11.0.1.2.0",
    "category": "Warehouse Management",
    "website": "http://bis2.binasanprima.com",
    "author": "erickalvino@gmail.com",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "material_transfer_in_out",
        "base_tier_validation",
    ],
    "data": [
        "data/material_transfer_tier_definition.xml",
        "views/material_transfer_view.xml",
    ],
}
