# -*- coding: utf-8 -*-
# © 2013 ZestyBeanz Technologies Pvt. Ltd.
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

try:
    import json
except ImportError:
    import simplejson as json
import openerp.addons.web.http as openerpweb
from openerp.addons.web.controllers.main import ExcelExport
from openerp.addons.web.controllers.main import Export
import re
from cStringIO import StringIO
from lxml import etree
import trml2pdf
import operator
import os
import openerp.tools as tools
try:
    import xlwt
except ImportError:
    xlwt = None


@openerpweb.jsonrequest
def formats(self, req):
    """
    Override the original method of class Export to prevent
    unwanted classes to appear in the types of exports in the
    exporting wizard.
    """
    return sorted([
        controller.fmt
        for path, controller in openerpweb.controllers_path.iteritems()
        if path.startswith(self._cp_path) and
        hasattr(controller, 'fmt') and
        controller.fmt is not None
    ], key=operator.itemgetter("label"))


Export.formats = formats
Export._cp_path = '/web/export'


class ZbExcelExport(ExcelExport):
    fmt = None

    _cp_path = '/web/export/zb_excel_export'

    def from_data(self, fields, rows):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        style = xlwt.easyxf('align: wrap yes')
        font = xlwt.Font()
        font.bold = True
        style.font = font
        ignore_index = []
        count = 0
        for i, fieldname in enumerate(fields):
            if fieldname.get('header_data_id', False):
                field_name = fieldname.get('header_name', '')
                worksheet.write(0, i - count, field_name, style)
                worksheet.col(i).width = 8000
            else:
                count += 1
                ignore_index.append(i)
        style = xlwt.easyxf('align: wrap yes')
        bold_style = xlwt.easyxf('align: wrap yes')
        font = xlwt.Font()
        font.bold = True
        bold_style.font = font
        for row_index, row in enumerate(rows):
            count = 0
            for cell_index, cell_value in enumerate(row):
                if cell_index not in ignore_index:
                    cell_style = style
                    if cell_value.get('bold', False):
                        cell_style = bold_style
                    cellvalue = cell_value.get('data', '')
                    if isinstance(cellvalue, basestring):
                        cellvalue = re.sub("\r", " ", cellvalue)
                    if cell_value.get('number', False) and cellvalue:
                        cellvalue = float(cellvalue)
                    if cellvalue is False:
                        cellvalue = None
                    worksheet.write(
                        row_index + 1, cell_index - count, cellvalue,
                        cell_style)
                else:
                    count += 1
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return data

    @openerpweb.httprequest
    def index(self, req, data, token):
        data = json.loads(data)
        return req.make_response(
            self.from_data(
                data.get('headers', []), data.get('rows', [])
            ),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                    % data.get('model', 'Export.xls')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )


class ExportPdf(Export):
    fmt = None
    _cp_path = '/web/export/zb_pdf'

    @property
    def content_type(self):
        return 'application/pdf'

    def filename(self, base):
        return base + '.pdf'

    def from_data(
        self, uid, fields, rows, company_name, company_logo, current_date
    ):
        """
        :param company_name: string
        :param company_logo: binary file
        """
        page_size = [210.0, 297.0]
        new_doc = etree.Element("report")
        config = etree.SubElement(new_doc, 'config')

        def _append_node(name, text):
            n = etree.SubElement(config, name)
            n.text = text
        _append_node('date', current_date)
        _append_node('PageSize', '%.2fmm,%.2fmm' % tuple(page_size))
        _append_node('PageWidth', '%.2f' % (page_size[0] * 2.8346,))
        _append_node('PageHeight', '%.2f' % (page_size[1] * 2.8346,))
        _append_node('PageFormat', 'a4')
        _append_node('header-date', current_date)
        _append_node('company', company_name)
        _append_node('company_logo', company_logo)

        skip_index = []
        header = etree.SubElement(new_doc, 'header')
        i = 0
        for f in fields:
            if f.get('header_data_id', False):
                value = f.get('header_name', "")
                field = etree.SubElement(header, 'field')
                field.text = tools.ustr(value)
            else:
                skip_index.append(i)
            i += 1
        lines = etree.SubElement(new_doc, 'lines')
        for row_lines in rows:
            node_line = etree.SubElement(lines, 'row')
            j = 0
            for row in row_lines:
                if j not in skip_index:
                    para = "yes"
                    tree = "no"
                    value = row.get('data', '')
                    if row.get('bold', False):
                        para = "group"
                    if row.get('number', False):
                        tree = "float"
                    col = etree.SubElement(
                        node_line, 'col', para=para, tree=tree)
                    col.text = tools.ustr(value)
                j += 1

        current_dir = os.path.dirname(os.path.abspath(__file__))
        transform = etree.XSLT(
            etree.parse(os.path.join(
                current_dir,
                'report/main_rml_layout.xsl'
            )))

        rml = etree.tostring(transform(new_doc))

        localcontext = {
            'company_logo': company_logo,
            'internal_header': False,
        }

        self.obj = trml2pdf.parseNode(
            rml, localcontext, title='Printscreen')
        return self.obj


class ZbPdfExport(ExportPdf):
    fmt = None
    _cp_path = '/web/export/zb_pdf_export'

    @openerpweb.httprequest
    def index(self, req, data, token):
        data = json.loads(data)
        uid = data.get('uid', False)

        return req.make_response(
            self.from_data(
                uid, data.get('headers', []),
                data.get('rows', []),
                data.get('company_name', ''),
                data.get('company_logo', ''),
                data.get('current_date', ''),
            ),
            headers=[
                ('Content-Disposition', 'attachment; filename=PDF Export'),
                ('Content-Type', self.content_type)],
            cookies={'fileToken': token}
        )
