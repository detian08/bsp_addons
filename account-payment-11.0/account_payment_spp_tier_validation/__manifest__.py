{
    "name": "SPP Tier Validation",
    "summary": "Extends the functionality of SPP  to "
               "support a tier validation process.",
    "version": "11.0.1.2.0",
    "category": "Account Payment",
    "website": "http://bis2.binasanprima.com",
    "author": "didin.komarudin@gmail.com",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base_tier_validation",
        "account_payment_spp" ,
    ],
    "data": [
        "data/spp_tier_definition.xml",
        "views/spp_view.xml",
    ],
}
