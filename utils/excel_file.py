import openpyxl
import pandas as pd
import wcwidth

from utils.logger import Logger


class ExcelFile(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def __enter__(self):
        self.writer = pd.ExcelWriter(self.path, engine='xlsxwriter')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.writer.close()

    def export_dataframe_to_excel(self, dataframe, sheet_name, string_columns: list = None, set_width_by_value=False):
        workbook = self.writer.book
        if sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name].clear()
        else:
            sheet = workbook.add_worksheet(sheet_name)
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#5B9BD5',
            'font_color': '#FFFFFF'
        })
        fmt_time = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        row = 1
        for i, row_data in dataframe.iterrows():
            for col_idx, col_value in enumerate(row_data):
                if pd.isna(col_value):
                    sheet.write(row, col_idx, None)
                elif isinstance(col_value, pd.Timestamp):
                    sheet.write_datetime(row, col_idx, col_value.to_pydatetime(), fmt_time)
                else:
                    col_name = dataframe.columns[col_idx]
                    if string_columns and col_name in string_columns:
                        sheet.write_string(row, col_idx, str(col_value))
                    else:
                        sheet.write(row, col_idx, col_value)
            row += 1
        worksheet = self.writer.sheets[sheet_name]
        if not isinstance(dataframe.columns, pd.RangeIndex):
            columns_width = [max(len(str(col)), wcwidth.wcswidth(str(col))) + 4 for col in dataframe.columns]
            for col_idx, col_name in enumerate(dataframe.columns):
                if set_width_by_value:
                    max_value_length = dataframe[col_name].astype(str).str.len().max()
                    columns_width[col_idx] = max(columns_width[col_idx], max_value_length)
                worksheet.set_column(col_idx, col_idx, columns_width[col_idx])
                worksheet.write(0, col_idx, col_name, header_format)

    def import_excel_to_dataframe(self):
        excel_file = pd.ExcelFile(self.path)
        visible_sheet_name = self.get_visible_sheet_name(excel_file)
        df = pd.read_excel(excel_file, sheet_name=visible_sheet_name)
        return df

    def get_visible_sheet_name(self, excel_file, index=0):
        sheets = openpyxl.load_workbook(excel_file, read_only=True).worksheets
        visible_sheets = []
        for sheet in sheets:
            if sheet.sheet_state != 'hidden':
                visible_sheets.append(sheet.title)
        if len(visible_sheets) != 1:
            error_info = f'{excel_file}: the excel file should contain only one visible sheet'
            Logger().error(error_info)
            raise Exception(error_info)
        return visible_sheets[index]
