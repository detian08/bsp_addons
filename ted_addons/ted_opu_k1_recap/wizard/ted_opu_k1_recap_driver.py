import base64
import os
import datetime
from datetime import datetime
from docxtpl import DocxTemplate
from odoo import api, fields, models
import platform
from zipfile import ZipFile
import xlwt


class TedOPUK1Out(models.Model):
    _name = 'purchase.request.tedopuk1.out'
    _description = 'Recap OPU & K1 Result'

    filename = fields.Char('Name', size=256)
    filedata = fields.Binary('Docx Report', readonly=True)


class TedOPUK1Wizard(models.Model):
    _name = 'purchase.request.tedopuk1.wizard'
    _description = 'Recap OPU-K1 Wizard'

    @api.multi
    def get_workbook(self):
        self.ensure_one()
        selected_order = self.env['purchase.request'].browse(self._context.get('active_ids', list()))
        workbook_value = xlwt.Workbook()
        nomor = 0

        for single_order in selected_order:
            counter += 1
            nomor += 1
            # initialize
            tanggal_terima = ''
            cabang = ''
            no_surat_k1 = ''
            tgl_k1_dibuat = ''
            no_opu = nominal = no_polisi = merk_type = tahun = km_akhir = km_ganti = ''
            jarak_km_penggunaan = jenis = spesifikasi_barang = qty = harga_satuan = harga_pengajuan = ''
            harga_acc = harga_pusat = selisih = percent_val = untuk = exp_spv = status = no_qcf = ''
            tgl_ke_bccd = keterangan_tambahan = periode = ''

            # assign value
            tanggal_terima = ''
            cabang = ''
            no_surat_k1 = ''
            tgl_k1_dibuat = ''
            no_opu = nominal = ''
            no_polisi = ''
            merk_type = ''
            tahun = ''
            km_akhir = ''
            km_ganti = ''
            jarak_km_penggunaan = ''
            jenis = ''
            spesifikasi_barang = ''
            qty = ''
            harga_satuan = ''
            harga_pengajuan = ''
            harga_acc = ''
            harga_pusat = ''
            selisih = ''
            percent_val = ''
            untuk = ''
            exp_spv = ''
            status = ''
            no_qcf = ''
            tgl_ke_bccd = ''
            keterangan_tambahan = ''
            periode = ''
            report_line_item = {'no': nomor,
                                'tanggal_terima': tanggal_terima,
                                'cabang': cabang,
                                'no_surat_k1': no_surat_k1,
                                'tgl_k1_dibuat': tgl_k1_dibuat,
                                'no_opu': no_opu,
                                'nominal': nominal,
                                'no_polisi': no_polisi,
                                'merk_type': merk_type,
                                'tahun': tahun,
                                'km_akhir': km_akhir,
                                'km_ganti': km_ganti,
                                'jarak_km_penggunaan': jarak_km_penggunaan,
                                'jenis': jenis,
                                'spesifikasi_barang': spesifikasi_barang,
                                'qty': qty,
                                'harga_satuan': harga_satuan,
                                'harga_pengajuan': harga_pengajuan,
                                'harga_acc': harga_acc,
                                'harga_pusat': harga_pusat,
                                'selisih': selisih,
                                'percent_val': percent_val,
                                'untuk': untuk,
                                'exp spv': exp_spv,
                                'status': status,
                                'no qcf': no_qcf,
                                'tgl_ke_bccd': tgl_ke_bccd,
                                'keterangan_tambahan': keterangan_tambahan,
                                'periode': periode,
                                }

            return workbook_value

    @api.multi
    def get_result(self):
        self.ensure_one()
        print_data = self.get_workbook()
        if print_data:
            result_filename = ''
            if platform.system() == 'Linux':
                result_filename = ('/tmp/TED_OPUK1-' + str(datetime.timestamp()) + '.xls')
            else:
                result_filename = ('/tmp/TED_OPUK1-' + str(datetime.timestamp()) + '.xls')
            result_filename =result_filename.split('/')[0]
            print_data.save(result_filename)
            file_handler = open(result_filename, "rb")
            result_data = file_handler.read()
            result_output = base64.encodestring(result_data)
            result_attachment = {
                'filename': result_filename,
                'filedata': result_output
            }
            result_object = self.env['purchase.request.docx.k1single'].create(result_attachment)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.request.opuk1.out',
                'res_id': result_object.id,
                'view_type': 'form',
                'view_mode': 'form',
                'context': self.env.context,
                'target': 'new',
            }
        else:
            return {}
