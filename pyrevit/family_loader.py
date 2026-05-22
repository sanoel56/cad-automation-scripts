# -*- coding: utf-8 -*-
"""Batch load families and swap types in Revit"""

import sys
import os
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from System.Collections.Generic import List
from pyrevit import revit, DB, UI
from pyrevit import script
from pyrevit import forms

# Get current document and app
doc = revit.doc
uidoc = revit.uidoc
app = doc.Application

# Create output logger
output = script.get_output()

# Helper function to get all family symbols from a family
def get_family_symbols(family):
    """Get all symbols (types) from a family"""
    symbols = FilteredElementCollector(doc).OfClass(FamilySymbol).WhereElementIsElementType()
    family_symbols = []
    for sym in symbols:
        if sym.Family.Id == family.Id:
            family_symbols.append(sym)
    return family_symbols

# Main function
def batch_load_and_swap():
    """Batch load families and swap types"""
    
    # Step 1: Select families to load
    output.print_md("## Step 1: Select families to load")
    
    # Get all loaded families in the document
    families = FilteredElementCollector(doc).OfClass(Family).ToElements()
    
    if not families:
        output.print_md("No families found in the document.")
        return
    
    # Let user select families to load (or load new ones)
    family_names = [f.Name for f in families]
    selected_family_names = forms.SelectFromList.show(
        family_names,
        title="Select families to load (or cancel to load new)",
        multiselect=True
    )
    
    if selected_family_names is None:
        # User wants to load new families
        output.print_md("### Loading new families...")
        
        # Ask user to select family files
        family_files = forms.pick_file(
            title="Select family files (.rfa)",
            file_filter="Revit Family Files (*.rfa)|*.rfa",
            multiselect=True
        )
        
        if not family_files:
            output.print_md("No files selected. Exiting.")
            return
        
        # Load families
        loaded_families = []
        with revit.Transaction("Batch Load Families"):
            for file_path in family_files:
                try:
                    family_name = os.path.basename(file_path).replace('.rfa', '')
                    # Check if family already exists
                    existing_family = None
                    for f in families:
                        if f.Name == family_name:
                            existing_family = f
                            break
                    
                    if existing_family:
                        output.print_md("Family '{}' already exists. Skipping.".format(family_name))
                        loaded_families.append(existing_family)
                    else:
                        # Load the family
                        family = doc.LoadFamily(file_path)
                        if family:
                            loaded_families.append(family)
                            output.print_md("Loaded family: {}".format(family_name))
                        else:
                            output.print_md("Failed to load family: {}".format(family_name))
                except Exception as e:
                    output.print_md("Error loading {}: {}".format(file_path, str(e)))
        
        if not loaded_families:
            output.print_md("No families loaded. Exiting.")
            return
        
        families = loaded_families
    else:
        # Filter families by selection
        families = [f for f in families if f.Name in selected_family_names]
        if not families:
            output.print_md("No families selected. Exiting.")
            return
        output.print_md("Selected {} families.".format(len(families)))
    
    # Step 2: Select source and target types
    output.print_md("## Step 2: Select source and target types")
    
    # Get all family symbols from selected families
    all_symbols = []
    for family in families:
        symbols = get_family_symbols(family)
        all_symbols.extend(symbols)
    
    if not all_symbols:
        output.print_md("No family symbols found. Exiting.")
        return
    
    # Let user select source type
    symbol_names = ["{} : {}".format(s.Family.Name, s.Name) for s in all_symbols]
    source_name = forms.SelectFromList.show(
        symbol_names,
        title="Select source type (type to swap FROM)",
        multiselect=False
    )
    
    if not source_name:
        output.print_md("No source type selected. Exiting.")
        return
    
    # Find source symbol
    source_symbol = None
    for s in all_symbols:
        if "{} : {}".format(s.Family.Name, s.Name) == source_name:
            source_symbol = s
            break
    
    if not source_symbol:
        output.print_md("Source type not found. Exiting.")
        return
    
    # Let user select target type
    target_name = forms.SelectFromList.show(
        symbol_names,
        title="Select target type (type to swap TO)",
        multiselect=False
    )
    
    if not target_name:
        output.print_md("No target type selected. Exiting.")
        return
    
    # Find target symbol
    target_symbol = None
    for s in all_symbols:
        if "{} : {}".format(s.Family.Name, s.Name) == target_name:
            target_symbol = s
            break
    
    if not target_symbol:
        output.print_md("Target type not found. Exiting.")
        return
    
    # Step 3: Find all instances of source type and swap
    output.print_md("## Step 3: Swapping instances...")
    
    # Collect all instances of source type
    instances = FilteredElementCollector(doc).OfClass(FamilyInstance).ToElements()
    source_instances = []
    for inst in instances:
        if inst.Symbol.Id == source_symbol.Id:
            source_instances.append(inst)
    
    if not source_instances:
        output.print_md("No instances of source type found in the document.")
        return
    
    output.print_md("Found {} instances of source type.".format(len(source_instances)))
    
    # Perform swap in a transaction
    with revit.Transaction("Batch Swap Types"):
        swapped_count = 0
        for inst in source_instances:
            try:
                inst.Symbol = target_symbol
                swapped_count += 1
            except Exception as e:
                output.print_md("Error swapping instance {}: {}".format(inst.Id, str(e)))
        
        output.print_md("Successfully swapped {} instances.".format(swapped_count))
    
    output.print_md("## Batch load and swap completed!")

# Run the main function
if __name__ == '__main__':
    batch_load_and_swap()