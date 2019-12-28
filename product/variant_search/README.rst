Search by variant attributes
============================

Enable search in product variants names instead then in product name only.
	  
This module has the following features and limits:
		
* When the variants are saved, we store the whole description in an internal field: product_product.var_desc.
		
* When searching for products, e.g. in invoice line, we perform search in that field.
		
* The "space" in search is a special character, so that "AA BB CC" will match both "AAAAABBBCCCC" and "BBBCCAAA" but not "AAAAA".
		
* Variant description is modified, attributes are ordered according to attributes' Sequence ordering, and not to alphabetic ordering.
		
* We do *not* search in customer's description! So this module is not compatible with companies using customer-specific descriptions.
		
* product_product.var_desc is a computed attribute stored on database, it's calculated during module install. If you want to recalculate it, the fast option is to reinstall this module.
