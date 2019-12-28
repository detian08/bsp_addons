from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    # on v9 value was stored on manually_set_invoiced
    openupgrade.logged_query(env.cr, """
        UPDATE purchase_order
        SET force_invoiced_status = 'invoiced'
        WHERE manually_set_invoiced = True
    """,)
    # on v9 value was stored on manually_set_received
    openupgrade.logged_query(env.cr, """
        UPDATE purchase_order
        SET force_delivered_status = 'received'
        WHERE manually_set_received = True
    """,)
