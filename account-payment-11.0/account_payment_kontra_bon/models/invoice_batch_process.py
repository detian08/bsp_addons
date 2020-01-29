from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

INV_TO_PARTN = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or
# goes out
INV_TO_PAYM_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"



    @api.model
    def default_get(self, pfields):
        """
        Get list of bills to pay
        """
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        kontrabon_number = context.get('kontrabon_number')
        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(
                _("Program error: wizard action executed without"
                  " active_model or active_ids in context."))
        if active_model != 'account.invoice':
            raise UserError(
                _("Program error: the expected model for this"
                  " action is 'account.invoice'. The provided one"
                  " is '%d'.") % active_model)

        # Checks on received invoice records
        invoices = self.env[active_model].browse(active_ids)
        if any(invoice.state != 'open' for invoice in invoices):
            raise UserError(
                _("You can only register payments for open invoices"))
        if any(INV_TO_PARTN[inv.type] != INV_TO_PARTN[invoices[0].type]
               for inv in invoices):
            raise UserError(
                _("You cannot mix customer invoices and vendor"
                  " bills in a single payment."))
        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(
                _("In order to pay multiple invoices at once, they"
                  " must use the same currency."))

        rec = {}
        if 'batch' in context and context.get('batch'):
            lines = []
            if INV_TO_PARTN[invoices[0].type] == 'customer':
                for inv in invoices:
                    dict_line = {
                        'partner_id': inv.partner_id.id,
                        'invoice_id': inv.id,
                        'balance_amt': inv.residual or 0.0,
                        'receiving_amt': inv.residual or 0.0,
                        'payment_difference': inv.residual or 0.0,
                        'handling': 'open'
                    }
                    lines.append((0, 0, dict_line))
                dict_val = {
                    'invoice_customer_payments': lines,
                    'is_customer': True
                }
                rec.update(dict_val)
            else:
                for inv in invoices:
                    dict_line = {
                        'partner_id': inv.partner_id.id,
                        'invoice_id': inv.id,
                        'balance_amt': inv.residual or 0.0,
                        # 'paying_amt': inv.residual or 0.0,
                        'paying_amt': inv.kontrabon_amount_payment or 0.0,
                    }
                    lines.append((0, 0, dict_line))
                dict_val = {
                    'invoice_payments': lines,
                    'is_customer': False
                }
                rec.update(dict_val)

        else:
            # Checks on received invoice records
            if any(INV_TO_PARTN[inv.type] != INV_TO_PARTN[invoices[0].type]
                   for inv in invoices):
                raise UserError(
                    _("You cannot mix customer invoices and"
                      " vendor bills in a single payment."))

        if 'batch' in context and context.get('batch'):
            total_amount = sum(
                inv.residual * INV_TO_PAYM_SIGN[inv.type] for inv in invoices)
                # inv.amount_payment * INV_TO_PAYM_SIGN[inv.type] for inv in invoices)

            dict_val_rec = {
                'amount': abs(total_amount),
                'currency_id': invoices[0].currency_id.id,
                'payment_type': total_amount > 0 and 'inbound' or 'outbound',
                'partner_id': invoices[0].commercial_partner_id.id,
                'partner_type': INV_TO_PARTN[invoices[0].type],
                'communication': kontrabon_number,
            }
            rec.update(dict_val_rec)
        else:
            rec = super(AccountRegisterPayments, self).default_get(pfields)

        return rec