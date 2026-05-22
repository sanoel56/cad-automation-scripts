# -*- coding: utf-8 -*-
"""Export Revit schedules to CSV/Excel."""

import sys
import os
import csv
from collections import OrderedDict

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System.Windows.Forms')

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB.Electrical import *
from Autodesk.Revit.DB.Mechanical import *
from Autodesk.Revit.DB.Plumbing import *
from Autodesk.Revit.DB.Structure import *
from Autodesk.Revit.DB.Architecture import *

from pyrevit import revit, DB, UI
from pyrevit import script
from pyrevit import forms

# Get current document
doc = revit.doc
uidoc = revit.uidoc

# Get all view schedules in the document
schedules = FilteredElementCollector(doc).OfClass(ViewSchedule).ToElements()

if not schedules:
    forms.alert('No schedules found in the document.', exitscript=True)

# Let user select schedules to export
selected_schedules = forms.SelectFromList.show(
    schedules,
    name_attr='Name',
    title='Select Schedules to Export',
    button_name='Export',
    multiselect=True
)

if not selected_schedules:
    script.exit()

# Ask for export format
format_options = ['CSV', 'Excel (XLSX)']
selected_format = forms.SelectFromList.show(
    format_options,
    title='Select Export Format',
    button_name='Select',
    multiselect=False
)

if not selected_format:
    script.exit()

# Ask for output folder
output_folder = forms.pick_folder()
if not output_folder:
    script.exit()

# Export each selected schedule
for schedule in selected_schedules:
    try:
        # Get schedule data
        table_data = schedule.GetTableData()
        section_data = table_data.GetSectionData(SectionType.Body)
        
        # Get number of rows and columns
        num_rows = section_data.NumberOfRows
        num_cols = section_data.NumberOfColumns
        
        # Prepare data matrix
        data = []
        for row_idx in range(num_rows):
            row_data = []
            for col_idx in range(num_cols):
                cell_value = section_data.GetCellText(schedule, row_idx, col_idx)
                row_data.append(cell_value)
            data.append(row_data)
        
        # Build file name
        schedule_name = schedule.Name
        # Remove invalid characters for file name
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            schedule_name = schedule_name.replace(char, '_')
        
        if selected_format == 'CSV':
            file_path = os.path.join(output_folder, schedule_name + '.csv')
            with open(file_path, 'wb') as csvfile:
                writer = csv.writer(csvfile)
                for row in data:
                    writer.writerow(row)
        else:  # Excel
            try:
                import xlsxwriter
            except ImportError:
                forms.alert('xlsxwriter module not found. Please install it or use CSV format.', exitscript=True)
            file_path = os.path.join(output_folder, schedule_name + '.xlsx')
            workbook = xlsxwriter.Workbook(file_path)
            worksheet = workbook.add_worksheet()
            for row_idx, row_data in enumerate(data):
                for col_idx, cell_value in enumerate(row_data):
                    worksheet.write(row_idx, col_idx, cell_value)
            workbook.close()
        
        print('Exported: {}'.format(file_path))
    except Exception as e:
        print('Error exporting schedule "{}": {}'.format(schedule.Name, str(e)))

print('Export complete.')
