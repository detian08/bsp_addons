{
    "name": "Kontra Bon Tier Validation",
    "summary": "Extends the functionality of Kontra Bon  to "
               "support a tier validation process.",
    "version": "11.0.1.2.0",
    "category": "Account Payment",
    "website": "http://bis2.binasanprima.com",
    "author": "didin.komarudin@gmail.com",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_payment_kontra_bon",
        "base_tier_validation",
    ],
    "data": [
        "data/kontra_bon_tier_definition.xml",
        "views/kontra_bon_view.xml",
    ],
}
