# -*- coding: utf-8 -*-
"""Bulk edit Revit parameters across hundreds of elements."""

import sys
import traceback

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('RevitServices')

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

# Get current document and UI application
doc = revit.doc
uidoc = revit.uidoc
app = revit.app

# Create output logger
output = script.get_output()

# Helper function to get parameter value as string
def get_param_value_string(param):
    """Return parameter value as string for display."""
    if param is None:
        return "<null>"
    if param.StorageType == StorageType.String:
        return param.AsString() or ""
    elif param.StorageType == StorageType.Integer:
        return str(param.AsInteger())
    elif param.StorageType == StorageType.Double:
        return str(param.AsDouble())
    elif param.StorageType == StorageType.ElementId:
        elem_id = param.AsElementId()
        if elem_id and elem_id != ElementId.InvalidElementId:
            elem = doc.GetElement(elem_id)
            if elem:
                return elem.Name
            else:
                return str(elem_id.IntegerValue)
        else:
            return "<none>"
    else:
        return "<unsupported>"

# Helper function to set parameter value
def set_param_value(param, value_str):
    """Set parameter value from string. Returns True if successful."""
    if param is None:
        return False
    try:
        if param.StorageType == StorageType.String:
            return param.Set(value_str)
        elif param.StorageType == StorageType.Integer:
            return param.Set(int(value_str))
        elif param.StorageType == StorageType.Double:
            # Try to parse as double, handle units if needed
            try:
                val = float(value_str)
            except:
                # Try to parse with unit string (e.g., "10 ft")
                val = UnitUtils.ParseAndConvertToInternalUnits(value_str, param.DisplayUnitType)
            return param.Set(val)
        elif param.StorageType == StorageType.ElementId:
            # Try to find element by name or id
            elem_id = None
            # Check if it's an integer (element id)
            try:
                int_val = int(value_str)
                elem_id = ElementId(int_val)
            except:
                # Try to find element by name
                collector = FilteredElementCollector(doc).WhereElementIsNotElementType()
                for elem in collector:
                    if elem.Name == value_str:
                        elem_id = elem.Id
                        break
                if elem_id is None:
                    # Try element types
                    collector = FilteredElementCollector(doc).WhereElementIsElementType()
                    for elem in collector:
                        if elem.Name == value_str:
                            elem_id = elem.Id
                            break
            if elem_id:
                return param.Set(elem_id)
            else:
                return False
        else:
            return False
    except Exception as e:
        output.print_exception(e)
        return False

# Main function
def main():
    # Step 1: Select elements
    selection = uidoc.Selection.GetElementIds()
    if not selection:
        # If nothing selected, ask user to select
        try:
            selection = uidoc.Selection.PickObjects(UI.Selection.ObjectType.Element, "Select elements to edit parameters")
            selection = [x.ElementId for x in selection]
        except:
            output.print_md("**Cancelled by user.**")
            return
    
    if not selection:
        output.print_md("**No elements selected. Exiting.**")
        return
    
    elements = [doc.GetElement(eid) for eid in selection]
    output.print_md("**Selected {} elements.**".format(len(elements)))
    
    # Step 2: Choose parameter
    # Collect all parameters from first element (or common parameters)
    first_elem = elements[0]
    param_dict = {}
    for param in first_elem.Parameters:
        if param.Definition:
            param_dict[param.Definition.Name] = param
    
    if not param_dict:
        output.print_md("**No parameters found on selected elements.**")
        return
    
    # Let user choose parameter
    param_names = sorted(param_dict.keys())
    chosen_param_name = forms.SelectFromList.show(
        param_names,
        title="Select Parameter to Edit",
        button_name="Select",
        multiselect=False
    )
    if not chosen_param_name:
        output.print_md("**Cancelled by user.**")
        return
    
    chosen_param = param_dict[chosen_param_name]
    
    # Step 3: Get current values and ask for new value
    current_values = []
    for elem in elements:
        param = elem.LookupParameter(chosen_param_name)
        if param:
            current_values.append(get_param_value_string(param))
        else:
            current_values.append("<missing>")
    
    # Show current values summary
    unique_values = set(current_values)
    output.print_md("**Current values for '{}':**".format(chosen_param_name))
    for val in unique_values:
        count = current_values.count(val)
        output.print_md("- {} ({} elements)".format(val, count))
    
    # Ask for new value
    new_value = forms.ask_for_string(
        prompt="Enter new value for parameter '{}':".format(chosen_param_name),
        title="Bulk Parameter Edit",
        default=""
    )
    if new_value is None:
        output.print_md("**Cancelled by user.**")
        return
    
    # Step 4: Apply changes with transaction
    t = Transaction(doc, "Bulk Edit Parameter: {}".format(chosen_param_name))
    t.Start()
    
    success_count = 0
    fail_count = 0
    failed_elements = []
    
    for elem in elements:
        param = elem.LookupParameter(chosen_param_name)
        if param and not param.IsReadOnly:
            if set_param_value(param, new_value):
                success_count += 1
            else:
                fail_count += 1
                failed_elements.append(elem.Id)
        else:
            fail_count += 1
            failed_elements.append(elem.Id)
    
    t.Commit()
    
    # Step 5: Report results
    output.print_md("**Operation completed.**")
    output.print_md("- Successfully updated: {} elements".format(success_count))
    output.print_md("- Failed: {} elements".format(fail_count))
    if failed_elements:
        output.print_md("**Failed element IDs:**")
        for eid in failed_elements:
            output.print_md("- {}".format(eid))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        output.print_exception(e)
        traceback.print_exc()