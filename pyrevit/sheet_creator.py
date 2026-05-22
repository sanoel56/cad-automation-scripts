# -*- coding: utf-8 -*-
"""Create sheets in bulk, place views, auto-name."""

import sys
import traceback

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from Autodesk.Revit.UI import *

from pyrevit import revit, DB, UI
from pyrevit import script
from pyrevit import forms

__doc__ = 'Create sheets in bulk, place views, auto-name'
__author__ = 'pyRevit Expert'
__title__ = 'Sheet Creator'
__context__ = 'zero-doc'

logger = script.get_logger()
output = script.get_output()

# Get current document
doc = revit.doc

if not doc:
    forms.alert('No active Revit document found.')
    sys.exit(0)

# Collect all views (excluding sheets, legends, schedules, etc.)
views = FEC(doc).OfClass(View).WhereElementIsNotElementType().ToElements()

# Filter out non-placeable views (e.g., drafting views, schedules, legends)
placeable_views = []
for v in views:
    if v.ViewType in [ViewType.FloorPlan, ViewType.CeilingPlan, ViewType.Elevation, ViewType.Section, ViewType.Detail, ViewType.ThreeD, ViewType.AreaPlan, ViewType.Rendering]:
        if not v.IsTemplate:
            placeable_views.append(v)

if not placeable_views:
    forms.alert('No placeable views found in the document.')
    sys.exit(0)

# Let user select views to place
selected_views = forms.SelectFromList.show(
    placeable_views,
    name_attr='Name',
    title='Select Views to Place on Sheets',
    button_name='Select',
    multiselect=True
)

if not selected_views:
    sys.exit(0)

# Ask for sheet parameters
sheet_prefix = forms.ask_for_string(
    prompt='Enter sheet number prefix (e.g., A-):',
    title='Sheet Number Prefix',
    default='A-'
)

if sheet_prefix is None:
    sys.exit(0)

sheet_title_base = forms.ask_for_string(
    prompt='Enter base sheet title (e.g., "Floor Plan"):',
    title='Sheet Title Base',
    default='Sheet'
)

if sheet_title_base is None:
    sys.exit(0)

# Ask for titleblock family type
titleblocks = FEC(doc).OfClass(FamilySymbol).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().ToElements()

if not titleblocks:
    forms.alert('No titleblocks loaded in the project.')
    sys.exit(0)

titleblock_options = {}
for tb in titleblocks:
    titleblock_options[tb.Name] = tb

tb_name = forms.SelectFromList.show(
    sorted(titleblock_options.keys()),
    title='Select Titleblock',
    button_name='Select'
)

if not tb_name:
    sys.exit(0)

titleblock_type = titleblock_options[tb_name]

# Start transaction
t = Transaction(doc, 'Create Sheets and Place Views')
t.Start()

try:
    created_sheets = []
    for i, view in enumerate(selected_views):
        # Create sheet
        sheet = ViewSheet.Create(doc, titleblock_type.Id)
        
        # Set sheet number and name
        sheet_number = '{}{:03d}'.format(sheet_prefix, i+1)
        sheet_name = '{} - {}'.format(sheet_title_base, view.Name)
        
        # Parameter handling
        param_number = sheet.get_Parameter(BuiltInParameter.SHEET_NUMBER)
        param_name = sheet.get_Parameter(BuiltInParameter.SHEET_NAME)
        
        if param_number:
            param_number.Set(sheet_number)
        if param_name:
            param_name.Set(sheet_name)
        
        # Place view on sheet
        # Get viewport type (default)
        viewport_types = FEC(doc).OfClass(ViewportType).WhereElementIsElementType().ToElements()
        if not viewport_types:
            raise Exception('No viewport types found.')
        viewport_type = viewport_types[0]
        
        # Create viewport at center of sheet
        # Get sheet outline
        outline = sheet.GetBoxCenter()
        # Place viewport at center (adjust as needed)
        viewport = Viewport.Create(doc, viewport_type.Id, view.Id, XYZ(outline.X, outline.Y, 0))
        
        created_sheets.append((sheet_number, sheet_name, view.Name))
    
    t.Commit()
    
    # Output results
    output.print_md('## Sheets Created Successfully')
    for sn, sname, vname in created_sheets:
        output.print_md('- Sheet **{}**: {} (View: {})'.format(sn, sname, vname))
    
    forms.alert('{} sheets created successfully.'.format(len(created_sheets)))

except Exception as e:
    t.RollBack()
    logger.error('Error creating sheets: {}'.format(str(e)))
    output.print_md('## Error')
    output.print_md('An error occurred: {}'.format(str(e)))
    forms.alert('Error creating sheets. Check output for details.')
    traceback.print_exc()