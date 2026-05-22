# -*- coding: utf-8 -*-
"""BIM Compliance Checker - Validate naming, parameters, standards"""

import sys
import traceback
from collections import defaultdict

import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

from pyrevit import revit, DB, UI
from pyrevit import script
from pyrevit import forms

# Get current document and output
output = script.get_output()
logger = script.get_logger()
doc = revit.doc

# Configuration - modify these as needed
CONFIG = {
    'naming_rules': {
        'Wall': r'^W\d{3}-[A-Z]{2,4}-.*$',
        'Floor': r'^F\d{3}-[A-Z]{2,4}-.*$',
        'Door': r'^D\d{3}-[A-Z]{2,4}-.*$',
        'Window': r'^W\d{3}-[A-Z]{2,4}-.*$'
    },
    'required_parameters': {
        'Wall': ['Comments', 'Mark', 'Fire Rating'],
        'Floor': ['Comments', 'Mark'],
        'Door': ['Comments', 'Mark', 'Fire Rating', 'Acoustic Rating'],
        'Window': ['Comments', 'Mark', 'Glazing Type']
    },
    'standards': {
        'Wall': {'Base Offset': 0.0, 'Top Offset': 0.0},
        'Floor': {'Height Offset From Level': 0.0}
    }
}

def get_all_elements_by_category(doc, category_builtin):
    """Get all elements of a given category."""
    collector = FilteredElementCollector(doc)
    category_filter = ElementCategoryFilter(category_builtin)
    return collector.WherePasses(category_filter).WhereElementIsNotElementType().ToElements()

def check_naming(element, rule):
    """Check if element name matches the naming rule."""
    import re
    name = element.Name
    if name:
        return bool(re.match(rule, name))
    return False

def check_parameters(element, required_params):
    """Check if element has all required parameters."""
    missing = []
    for param_name in required_params:
        param = element.LookupParameter(param_name)
        if param is None:
            missing.append(param_name)
        else:
            # Check if parameter has a value (optional)
            if param.HasValue:
                pass  # Value exists
            else:
                missing.append(param_name + " (no value)")
    return missing

def check_standards(element, standards):
    """Check if element meets standard parameter values."""
    violations = []
    for param_name, expected_value in standards.items():
        param = element.LookupParameter(param_name)
        if param:
            try:
                if param.StorageType == StorageType.Double:
                    actual_value = param.AsDouble()
                    if abs(actual_value - expected_value) > 0.001:
                        violations.append("{}: expected {}, got {}".format(param_name, expected_value, actual_value))
                elif param.StorageType == StorageType.Integer:
                    actual_value = param.AsInteger()
                    if actual_value != expected_value:
                        violations.append("{}: expected {}, got {}".format(param_name, expected_value, actual_value))
                elif param.StorageType == StorageType.String:
                    actual_value = param.AsString()
                    if actual_value != expected_value:
                        violations.append("{}: expected '{}', got '{}'".format(param_name, expected_value, actual_value))
            except Exception as e:
                violations.append("Error checking {}: {}".format(param_name, str(e)))
        else:
            violations.append("Parameter '{}' not found".format(param_name))
    return violations

def main():
    """Main execution function."""
    output.print_md("# BIM Compliance Checker")
    output.print_md("---")
    
    # Mapping of category names to BuiltInCategory
    category_map = {
        'Wall': BuiltInCategory.OST_Walls,
        'Floor': BuiltInCategory.OST_Floors,
        'Door': BuiltInCategory.OST_Doors,
        'Window': BuiltInCategory.OST_Windows
    }
    
    results = defaultdict(list)
    
    # Start a transaction for read-only operations (not necessary but safe)
    t = Transaction(doc, "BIM Compliance Check")
    t.Start()
    
    try:
        for category_name, builtin_cat in category_map.items():
            elements = get_all_elements_by_category(doc, builtin_cat)
            output.print_md("## Checking {} ({} elements)".format(category_name, len(elements)))
            
            naming_rule = CONFIG['naming_rules'].get(category_name)
            required_params = CONFIG['required_parameters'].get(category_name, [])
            standards = CONFIG['standards'].get(category_name, {})
            
            for elem in elements:
                elem_id = elem.Id
                elem_name = elem.Name
                issues = []
                
                # Check naming
                if naming_rule:
                    if not check_naming(elem, naming_rule):
                        issues.append("Naming violation: '{}' does not match pattern {}".format(elem_name, naming_rule))
                
                # Check parameters
                if required_params:
                    missing = check_parameters(elem, required_params)
                    if missing:
                        issues.append("Missing parameters: {}".format(', '.join(missing)))
                
                # Check standards
                if standards:
                    violations = check_standards(elem, standards)
                    if violations:
                        issues.append("Standard violations: {}".format('; '.join(violations)))
                
                if issues:
                    results[category_name].append((elem_id, elem_name, issues))
                    output.print_md("- **{}** (ID: {}):".format(elem_name, elem_id))
                    for issue in issues:
                        output.print_md("  - {}".format(issue))
        
        t.Commit()
        
        # Summary
        output.print_md("---")
        output.print_md("## Summary")
        total_issues = sum(len(v) for v in results.values())
        output.print_md("Total elements with issues: {}".format(total_issues))
        for cat, items in results.items():
            output.print_md("- {}: {} elements".format(cat, len(items)))
        
        if total_issues == 0:
            output.print_md("### All elements passed compliance checks!")
        
    except Exception as e:
        t.RollBack()
        logger.error("Error during compliance check: {}".format(str(e)))
        output.print_md("**Error:** {}".format(str(e)))
        traceback.print_exc()

if __name__ == '__main__':
    main()