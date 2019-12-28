# Output example
#
# Purchase Request
#
# Nomor    : PR00041
# Tanggal  : 2019-09-08
# Cabang   : My Company
#
# -----------------------------------------------------------------------------------------------
#  No. Nama                 Jumlah satuan keterangan           spesifikasi             Est.Harga
# -----------------------------------------------------------------------------------------------
#  1 AC Repair                 5 Unit(s) AC Bagian Tengah     POWER 10 dan 12      5.000.000,00
#  2 Radiator                  5 Unit(s) Radiator Ganti Full  RAD TIPE HONDA CITY  9.000.000,00
# -----------------------------------------------------------------------------------------------
#                                                                           TOTAL 14.000.000,00

# import platform
# if platform.system() == 'Windows':
# elif platform.system() == 'Linux':
# else:
#    raise Exception("Sorry: no implementation for your platform ('%s') available" % platform.system())

import locale
import os
from mako.lookup import TemplateLookup
from odoo import models, api

locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
tlookup = TemplateLookup(directories=[os.path.dirname(__file__)])


def money(n):
    return locale.format('%.2f', n, True)


class WizardPurchaseRequest(models.Model):
    _name = 'wizard.purchase.request.print'
    _description = "purchase request print wizard"

    @api.multi
    def print_report(self):
        self.ensure_one()
        order = self.env['purchase.request'].browse(self._context.get('active_ids', list()))
        tline = tlookup.get_template('purchase_request_line.txt')
        for rec in order:
            no = 0
            rows = []
            amount_total = 0
            for line in rec.line_ids:
                no += 1
                amount_total += line.estimated_cost
                s = tline.render(no=str(no),
                                 product_name=str(line.product_id.name),
                                 qty=str(int(line.product_qty)),
                                 uom=str(line.product_uom_id.name),
                                 desc=str(line.name),
                                 spec=str(line.specifications),
                                 estcost=str(money(line.estimated_cost)))
                rows.append(s)
            thead = tlookup.get_template('purchase_request.txt')
            s = thead.render(nomor=str(rec.name),
                             tgl=str(rec.date_start),
                             cabang=(rec.company_id.name),
                             rows=''.join(rows),
                             total=str(money(amount_total).rjust(12)))
            # filename= '/dev/lp0' --> linux
            filename = 'D:/tmp/%s_%s.txt' % (str(rec.name), str(self.env.uid))
            f = open(filename, 'w')
            f.write(s)
            # os.startfile(filename, "print")
            f.close()
        return {}
