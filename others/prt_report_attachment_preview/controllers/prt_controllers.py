from odoo import http
from odoo.http import request, Response
from odoo.addons.web.controllers.main import ReportController, Binary
import werkzeug

# List of content types that will be opened in browser
OPEN_BROWSER_TYPES = ['application/pdf']


######################
# Report Controllers #
######################
class PrtReportController(ReportController):

    @http.route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token):
        res = super(PrtReportController, self).report_download(data, token)
        res.headers['Content-Disposition'] = res.headers['Content-Disposition'].replace('attachment', 'inline')
        return res


######################
# Binary Controllers #
######################
class PrtBinaryController(Binary):
    @http.route(['/web/content',
        '/web/content/<string:xmlid>',
        '/web/content/<string:xmlid>/<string:filename>',
        '/web/content/<int:id>',
        '/web/content/<int:id>/<string:filename>',
        '/web/content/<int:id>-<string:unique>',
        '/web/content/<int:id>-<string:unique>/<string:filename>',
        '/web/content/<string:model>/<int:id>/<string:field>',
        '/web/content/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="public")
    def content_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       filename=None, filename_field='datas_fname', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None, **kw):

        res = super(PrtBinaryController, self).content_common(xmlid=xmlid, model=model, id=id, field=field,
                                                              filename=filename, filename_field=filename_field,
                                                              unique=unique, mimetype=mimetype,
                                                              download=download, data=data, token=token,
                                                              access_token=access_token, **kw)
        if download:
            if res.headers.get('Content-type', 'other') in OPEN_BROWSER_TYPES:
                res.headers['Content-Disposition'] = res.headers['Content-Disposition'].replace('attachment', 'inline')
        return res
