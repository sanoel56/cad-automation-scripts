# -*- coding: utf-8 -*-
"""Extract room data (name, area, volume) to Excel."""

import sys
import os
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System.Windows.Forms')

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from System.Collections.Generic import List
from System.Windows.Forms import SaveFileDialog, DialogResult

# pyRevit imports
from pyrevit import revit, DB, UI
from pyrevit import script
from pyrevit import forms

# Excel export (using CSV for simplicity, can be adapted to xlsx)
import csv

__doc__ = 'Extract room data (name, area, volume) to Excel'
__title__ = 'Room Data to Excel'
__author__ = 'pyRevit User'
__helpurl__ = ''

logger = script.get_logger()
output = script.get_output()

# Get current document
doc = revit.doc

# Collect all rooms from the active document
rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

if not rooms:
    forms.alert('No rooms found in the current document.', exitscript=True)

# Prepare data list
data = []
for room in rooms:
    try:
        name = room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString() or ''
        area = room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble()
        volume = room.get_Parameter(BuiltInParameter.ROOM_VOLUME).AsDouble()
        # Convert from square feet / cubic feet to desired units (optional)
        # For simplicity, keep in Revit internal units (feet)
        data.append([name, area, volume])
    except Exception as e:
        logger.warning('Could not extract data for room {}: {}'.format(room.Id, str(e)))

if not data:
    forms.alert('No room data could be extracted.', exitscript=True)

# Ask user for save location
save_dialog = SaveFileDialog()
save_dialog.Title = 'Save Room Data'
save_dialog.Filter = 'CSV Files (*.csv)|*.csv|All Files (*.*)|*.*'
save_dialog.FilterIndex = 1
save_dialog.RestoreDirectory = True

if save_dialog.ShowDialog() == DialogResult.OK:
    file_path = save_dialog.FileName
    try:
        with open(file_path, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Room Name', 'Area (sq ft)', 'Volume (cu ft)'])
            writer.writerows(data)
        output.print_success('Room data exported to: {}'.format(file_path))
    except Exception as e:
        logger.error('Failed to write CSV: {}'.format(str(e)))
        forms.alert('Failed to export data. Check pyRevit output for details.', exitscript=True)
else:
    forms.alert('Export cancelled.', exitscript=True)
