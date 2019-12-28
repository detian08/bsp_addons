# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Request Tier Validation Extend",
    "summary": "Extends the functionality of Purchase Requests to "
               "support a tier validation process.",
    "version": "11.0.1.1.0",
    "category": "Purchase Management",
    "website": "http:www.binasanprima.com",
    "author": "erickalvino@gmail.com",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase_request",
        "base_tier_validation",
    ],
    "data": [
        "data/purchase_request_tier_definition.xml",
        "views/purchase_request_view.xml",
    ],
}
