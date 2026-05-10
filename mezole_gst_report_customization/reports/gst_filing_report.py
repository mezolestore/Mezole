from odoo import fields,models, _
from datetime import datetime
import math
from odoo.exceptions import UserError


class GstFilingReport(models.AbstractModel):
    _name = 'report.mezole_gst_report_customization.gst_filing_report_xlsx'
    _description ='GST Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        date_to = wizard.to_date
        date_from = wizard.from_date
    
        heading_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 18, 'bg_color': '#0077b3', 'font_color': '#FFFFFF'})
        sub_heading_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12, 'bg_color': '#0077b3', 'font_color': '#FFFFFF'})
        col_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'font_color': '#FFFFFF', 'bg_color': '#0077b3', 'bold': True, 'size': 10})
        data_format = workbook.add_format({'align': 'center', 'valign': 'top'})
        date_format = workbook.add_format({'align': 'center', 'valign': 'top', 'num_format': 'dd/mm/yyyy'})
    
        company_name = self.env.company.name
        worksheet = workbook.add_worksheet(f'GST Report- {company_name}')
    
        # Set column widths
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 15)
        worksheet.set_column('L:L', 15)
        worksheet.set_column('M:M', 15)
        # Sub-headings for date range
        worksheet.merge_range(3, 0, 3, 1, "Date From", sub_heading_format)
        worksheet.write(3, 2, "Date To", sub_heading_format)
    
        from_date = wizard.from_date.strftime("%Y-%m-%d")
        to_date = wizard.to_date.strftime("%Y-%m-%d")
        worksheet.merge_range(4, 0, 4, 1, from_date, data_format)
        worksheet.write(4, 2, to_date, data_format)
    
        row = 6  # Start row for data
    
        if wizard.types == 'invoice':
            worksheet.merge_range('A1:L2', f'GST Invoice Report - {company_name}', heading_format)
            # Fetch invoices within the date range
            b2b_invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', date_from),
                ('invoice_date', '<=', date_to),
                ('state', '=', 'posted'),
                ('l10n_in_gst_treatment', '=', 'regular')
            ])
            if b2b_invoices:
                # B2B Invoices
                worksheet.merge_range(row, 0, row, 7, 'B2B Invoices', heading_format)
                row += 2
                # Collect all unique tax rates
                tax_rates = {}
                for invoice in b2b_invoices:
                    for line in invoice.invoice_line_ids:
                        for tax in line.tax_ids:
                            if tax.children_tax_ids:
                                for child in tax.children_tax_ids:
                                    child_rate = tax.amount
                                    if child_rate not in tax_rates:
                                        tax_rates[child_rate] = {'taxable_value': 0, 'igst': 0, 'cgst': 0, 'sgst': 0}
                            else:
                                rate = tax.amount
                                if rate not in tax_rates:
                                    tax_rates[rate] = {'taxable_value': 0, 'igst': 0, 'cgst': 0, 'sgst': 0}
    
                # Sort tax rates
                sorted_tax_rates = sorted(tax_rates.keys())
                # Create dynamic headers
                headers = ['Invoice No', 'Party', 'Invoice Date', 'GSTIN']
                start_col = 4
                for rate in sorted_tax_rates:
                    worksheet.merge_range(row, start_col, row, start_col + 3, f'{rate}%', sub_heading_format)
                    worksheet.write(row + 1, start_col, 'Taxable Value', sub_heading_format)
                    worksheet.write(row + 1, start_col + 1, 'IGST', sub_heading_format)
                    worksheet.write(row + 1, start_col + 2, 'CGST', sub_heading_format)
                    worksheet.write(row + 1, start_col + 3, 'SGST', sub_heading_format)
                    start_col += 4
    
                worksheet.write_row(row, 0, headers, sub_heading_format)
    
                # Populate data rows
                row += 3
                for invoice in b2b_invoices:
                    col = 0
                    worksheet.write(row, col, invoice.name)
                    worksheet.write(row, col + 1, invoice.partner_id.name)
                    worksheet.write(row, col + 2, str(invoice.invoice_date))
                    worksheet.write(row, col + 3, invoice.partner_id.vat)
    
                    # Initialize tax data
                    tax_data = {rate: {'taxable_value': 0, 'igst': 0, 'cgst': 0, 'sgst': 0} for rate in sorted_tax_rates}
    
                    # Aggregate tax data
                    for line in invoice.invoice_line_ids:
                        for tax in line.tax_ids:
                            if tax.children_tax_ids:
                                for child in tax.children_tax_ids:
                                    rate = tax.amount
                                    if 'igst' in child.name.lower():
                                        tax_data[rate]['igst'] += round((child.amount / 100) * line.price_subtotal, 2)
                                    elif 'sgst' in child.name.lower():
                                        tax_data[rate]['sgst'] += round((child.amount / 100) * line.price_subtotal, 2)
                                    elif 'cgst' in child.name.lower():
                                        tax_data[rate]['cgst'] += round((child.amount / 100) * line.price_subtotal, 2)
                                tax_data[rate]['taxable_value'] += line.price_subtotal
                            else:
                                rate = tax.amount
                                if 'igst' in tax.name.lower():
                                    tax_data[rate]['igst'] += round((tax.amount / 100) * line.price_subtotal, 2)
                                elif 'sgst' in tax.name.lower():
                                    tax_data[rate]['sgst'] += round((tax.amount / 100) * line.price_subtotal, 2)
                                elif 'cgst' in tax.name.lower():
                                    tax_data[rate]['cgst'] += round((tax.amount / 100) * line.price_subtotal, 2)
                                tax_data[rate]['taxable_value'] += line.price_subtotal
    
                    # Write tax data to worksheet
                    start_col = 4
                    for rate in sorted_tax_rates:
                        worksheet.write(row, col + start_col, tax_data[rate]['taxable_value'])
                        worksheet.write(row, col + start_col + 1, tax_data[rate]['igst'])
                        worksheet.write(row, col + start_col + 2, tax_data[rate]['cgst'])
                        worksheet.write(row, col + start_col + 3, tax_data[rate]['sgst'])
                        start_col += 4
    
                    row += 1
    
            row += 2  # Adding space between B2B and B2C sections
    
            # Fetch invoices within the date range
            b2c_invoices = self.env['account.move'].search([
                ('move_type', 'in', ['out_invoice','out_refund']),
                ('invoice_date', '>=', date_from),
                ('invoice_date', '<=', date_to),
                ('state', '=', 'posted'),
                ('l10n_in_gst_treatment', '!=', 'regular')
            ])
    
            if b2c_invoices:
                
                # B2C Invoices
                worksheet.merge_range(row, 0, row, 7, 'B2C Invoices', heading_format)
                row += 2
                # Collect all unique tax rates
                tax_rates = {}
                for invoice in b2c_invoices:
                    for line in invoice.invoice_line_ids:
                        for tax in line.tax_ids:
                            if tax.children_tax_ids:
                                for child in tax.children_tax_ids:
                                    child_rate = tax.amount
                                    if child_rate not in tax_rates:
                                        tax_rates[child_rate] = {'taxable_value': 0, 'igst': 0, 'cgst': 0, 'sgst': 0}
                            else:
                                rate = tax.amount
                                if rate not in tax_rates:
                                    tax_rates[rate] = {'taxable_value': 0, 'igst': 0, 'cgst': 0, 'sgst': 0}
    
                # Sort tax rates
                sorted_tax_rates = sorted(tax_rates.keys())
                # Create dynamic headers
                headers = ['Invoice No11111', 'Party', 'Invoice Date', 'GSTIN']
                start_col = 4
                for rate in sorted_tax_rates:
                    worksheet.merge_range(row, start_col, row, start_col + 3, f'{rate}%', sub_heading_format)
                    worksheet.write(row + 1, start_col, 'Taxable Value', sub_heading_format)
                    worksheet.write(row + 1, start_col + 1, 'IGST', sub_heading_format)
                    worksheet.write(row + 1, start_col + 2, 'CGST', sub_heading_format)
                    worksheet.write(row + 1, start_col + 3, 'SGST', sub_heading_format)
                    start_col += 4
    
                worksheet.write_row(row, 0, headers, sub_heading_format)
    
                # Populate data rows
                row += 3
                for invoice in b2c_invoices:
                    col = 0
                    worksheet.write(row, col, invoice.name)
                    worksheet.write(row, col + 1, invoice.partner_id.name)
                    worksheet.write(row, col + 2, str(invoice.invoice_date))
                    worksheet.write(row, col + 3, invoice.partner_id.vat)
    
                    # Initialize tax data
                    tax_data = {rate: {'taxable_value': 0, 'igst': 0, 'cgst': 0, 'sgst': 0} for rate in sorted_tax_rates}
    
                    # Aggregate tax data
                    for line in invoice.invoice_line_ids:
                        for tax in line.tax_ids:
                            if tax.children_tax_ids:
                                for child in tax.children_tax_ids:
                                    rate = tax.amount
                                    if 'igst' in child.name.lower():
                                        tax_data[rate]['igst'] += round((child.amount / 100) * line.price_subtotal, 2)
                                    elif 'sgst' in child.name.lower():
                                        tax_data[rate]['sgst'] += round((child.amount / 100) * line.price_subtotal, 2)
                                    elif 'cgst' in child.name.lower():
                                        tax_data[rate]['cgst'] += round((child.amount / 100) * line.price_subtotal, 2)
                                tax_data[rate]['taxable_value'] += line.price_subtotal
                            else:
                                rate = tax.amount
                                if 'igst' in tax.name.lower():
                                    tax_data[rate]['igst'] += round((tax.amount / 100) * line.price_subtotal, 2)
                                elif 'sgst' in tax.name.lower():
                                    tax_data[rate]['sgst'] += round((tax.amount / 100) * line.price_subtotal, 2)
                                elif 'cgst' in tax.name.lower():
                                    tax_data[rate]['cgst'] += round((tax.amount / 100) * line.price_subtotal, 2)
                                tax_data[rate]['taxable_value'] += line.price_subtotal
    
                    # Write tax data to worksheet
                    start_col = 4
                    for rate in sorted_tax_rates:
                        worksheet.write(row, col + start_col, tax_data[rate]['taxable_value'])
                        worksheet.write(row, col + start_col + 1, tax_data[rate]['igst'])
                        worksheet.write(row, col + start_col + 2, tax_data[rate]['cgst'])
                        worksheet.write(row, col + start_col + 3, tax_data[rate]['sgst'])
                        start_col += 4
    
                    row += 1
    
        if wizard.types == 'hsn':
            worksheet.merge_range('A1:G2', f'GST HSN Report - {company_name}', heading_format)
            row = 6
            b2b_invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', date_from),
                ('invoice_date', '<=', date_to),
                ('state', '=', 'posted'),
                ('l10n_in_gst_treatment', '=', 'regular')
            ])
            
            b2c_invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', date_from),
                ('invoice_date', '<=', date_to),
                ('state', '=', 'posted'),
                ('l10n_in_gst_treatment', '!=', 'regular')
            ])
        
            # Function to handle HSN grouping and tax calculation
            def process_invoices(invoices, worksheet, row, title):
                # Initialize a dictionary to hold aggregated data by HSN code and tax rate
                hsn_data = {}
        
                for invoice in invoices:
                    for line in invoice.invoice_line_ids:
                        hsn_code = line.product_id.l10n_in_hsn_code
                        for tax in line.tax_ids:
                            tax_rate = tax.amount
                            
                            if (hsn_code, tax_rate) not in hsn_data:
                                hsn_data[(hsn_code, tax_rate)] = {
                                    'taxable_value': 0,
                                    'igst': 0,
                                    'cgst': 0,
                                    'sgst': 0,
                                    'quantity': 0
                                }
        
                            # Aggregate data by HSN code and tax rate
                            hsn_data[(hsn_code, tax_rate)]['taxable_value'] += line.price_subtotal
                            hsn_data[(hsn_code, tax_rate)]['quantity'] += line.quantity
                            
                            if tax.children_tax_ids:
                                for child in tax.children_tax_ids:
                                    if 'igst' in child.name.lower():
                                        hsn_data[(hsn_code, tax_rate)]['igst'] += round((child.amount / 100) * line.price_subtotal, 2)
                                    elif 'sgst' in child.name.lower():
                                        hsn_data[(hsn_code, tax_rate)]['sgst'] += round((child.amount / 100) * line.price_subtotal, 2)
                                    elif 'cgst' in child.name.lower():
                                        hsn_data[(hsn_code, tax_rate)]['cgst'] += round((child.amount / 100) * line.price_subtotal, 2)
                            else:
                                if 'igst' in tax.name.lower():
                                    hsn_data[(hsn_code, tax_rate)]['igst'] += round((tax.amount / 100) * line.price_subtotal, 2)
                                elif 'sgst' in tax.name.lower():
                                    hsn_data[(hsn_code, tax_rate)]['sgst'] += round((tax.amount / 100) * line.price_subtotal, 2)
                                elif 'cgst' in tax.name.lower():
                                    hsn_data[(hsn_code, tax_rate)]['cgst'] += round((tax.amount / 100) * line.price_subtotal, 2)
                
                # Determine the columns based on the presence of tax values
                has_igst = any(values['igst'] > 0 for values in hsn_data.values())
                has_cgst = any(values['cgst'] > 0 for values in hsn_data.values())
                has_sgst = any(values['sgst'] > 0 for values in hsn_data.values())
        
                # Header preparation
                headers = ['HSN Code', 'Taxable Value', 'Tax Rate']
                if has_igst:
                    headers.append('IGST')
                if has_cgst:
                    headers.append('CGST')
                if has_sgst:
                    headers.append('SGST')
                headers.append('Quantity(Nos)')
                
                # Write the header
                worksheet.merge_range(row, 0, row, len(headers) - 1, title, heading_format)
                row += 1
                worksheet.write_row(row, 0, headers, sub_heading_format)
                row += 1
        
                # Write the data
                for (hsn_code, tax_rate), values in hsn_data.items():
                    row_data = [hsn_code, values['taxable_value'], f"{tax_rate}%"]
                    if has_igst:
                        row_data.append(values['igst'])
                    if has_cgst:
                        row_data.append(values['cgst'])
                    if has_sgst:
                        row_data.append(values['sgst'])
                    row_data.append(values['quantity'])
        
                    worksheet.write_row(row, 0, row_data)
                    row += 1
                
                return row + 2  # Add space between sections
        
            # Process B2B Invoices
            if b2b_invoices:
                row = process_invoices(b2b_invoices, worksheet, row, 'B2B Invoices')
        
            # Process B2C Invoices
            if b2c_invoices:
                row = process_invoices(b2c_invoices, worksheet, row, 'B2C Invoices')
