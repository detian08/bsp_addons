# Output example
#                              QUOTATION COMPARISON FORM
#
#                   No: QCF001                      Date : 10/10/2019
# ----------------------------------------------------------------------------------------------
# Material/Item         : UPS CT1328                                Code No      : M010
# BPPB No & Date        : BPPB/2019/001 - 10/20/2019                Qunatity     : 1 unit
# Head Office/ Branch   : Bogor                                     Approx Value : 2.500.000
# Departemen            : Sales
# -----------------------------------------------------------------------------------------------
#  No.  Supplier - Place                                Net Price (Rp)          Payment Term
# -----------------------------------------------------------------------------------------------
#  1    Pengajuan-Cabang                                2.700.000                       0 days
#  2    BIZ Media - Bandung                             2.500.000                       7 days
#  3    PT Tunggal Perkasa                              2.550.000                       7 days
# -----------------------------------------------------------------------------------------------
#  Detail Last Procurement
#  Supplier     : BIZ Media
#  Price        : 2.400.000
#  Po No & Data : PO001 & 08/08/2019
#
#  Pesanan for Buying
#
#
#

import locale
import os
from mako.lookup import TemplateLookup
from odoo import models, api

# locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
tlookup = TemplateLookup(directories=[os.path.dirname(__file__)])


def money(n):
    return locale.format('%.2f', n, True)


class WizardPurchaseRequisition(models.Model):
    _name = 'wizard.purchase.requisition.print'
    _description = "purchase requisition print wizard"

    @api.multi
    def print_report(self):
        self.ensure_one()
        order = self.env['purchase.requisition'].browse(self._context.get('active_ids', list()))
        tline = tlookup.get_template('purchase_requisition_line.txt')
        for rec in order:
            no = 0
            rows = []
           # amount_total = 0
            product_name=''
            for line in rec.line_ids:
                product_name += str(line.product_id.name) + " "
                bppbku = 1

                #bppbku = line.purchase_request_lines.request_id.id
            for line in rec.purchase_ids:
                no += 1
                s = tline.render(no=str(no),
                                 vendor_name=str(line.partner_id.name),
                                 amount_total=str(int(line.amount_total)),
                                 payment_term=str(line.payment_term_id.name))
                rows.append(s)

            thead = tlookup.get_template('purchase_requisition.txt')
            s = thead.render(nomor=str(rec.name),
                             bppbku = 1,
                             product_name = product_name,
                             cabang=(rec.company_id.name),
                             rows=''.join(rows))
            #                 total=str(money(amount_total).rjust(12)))
            # filename= '/dev/lp0' --> linux
            filename = r'D:/tmp/%s_%s.txt' % (str(rec.name), str(self.env.uid))
            f = open(filename, 'w')
            f.write(s)
            #os.startfile(filename, "print")
            f.close()
        return {}
