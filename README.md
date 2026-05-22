# AutoCAD & Revit Automation Scripts

Custom **AutoLISP** and **pyRevit** scripts for architects, engineers, and BIM professionals.  
These scripts automate repetitive CAD tasks — batch rename layers, count blocks, export schedules, and more.

## Scripts

### AutoCAD LISP (.lsp)
| Script | Command | What it does |
|--------|---------|-------------|
| `batch_layer_manager.lsp` | `BATCHLAYER` | Batch rename layers with prefix (skips 0 & Defpoints) |
| `block_counter.lsp` | `BLKCOUNT` | Count blocks and display in a table / export to CSV |
| `coordinate_extractor.lsp` | `EXPORTCOORDS` | Export point coordinates (X,Y,Z) to CSV file |
| `layout_manager.lsp` | `LAYOUTMGR` | Batch rename, reorder, create, delete layouts |
| `attribute_editor.lsp` | `ATTRIBULK` | Extract and update block attributes in bulk |
| `annotation_scale.lsp` | `SETANNO` | Auto-set annotative scales for text, dims, blocks |
| `polyline_area.lsp` | `POLYAREA` | Calculate and schedule polyline areas and lengths |

### pyRevit (Python for Revit)
| Script | What it does |
|--------|-------------|
| `schedule_export.py` | Export Revit schedules to CSV/Excel |
| `bulk_parameter.py` | Bulk edit parameters across hundreds of elements |
| `sheet_creator.py` | Create sheets in bulk, place views, auto-name |
| `room_data.py` | Extract room data (name, area, volume) to Excel |
| `bim_compliance.py` | Validate elements follow naming/parameter standards |
| `family_loader.py` | Batch load families and swap types |

## How to use

### AutoCAD LISP
1. Open AutoCAD, type `APPLOAD`
2. Select the `.lsp` file → click **Load**
3. Type the command name (e.g., `BATCHLAYER`) and follow prompts

### pyRevit
1. Install [pyRevit](https://pyrevitlabs.io/)
2. Place the `.py` file in your custom extension folder
3. Restart Revit — the script appears as a button in the pyRevit tab

## Pricing

| Service | Price | Delivery |
|---------|-------|---------|
| Simple LISP script | $50 | 24 hours |
| Medium LISP script | $100 | 48 hours |
| Complex LISP script | $200 | 3-5 days |
| Simple pyRevit script | $100 | 48 hours |
| Complex pyRevit script | $400 | 5-7 days |
| Custom automation (hourly) | $60/hr | Varies |

## Need a custom script?

Open an issue or contact me on:
- **Upwork**: https://www.upwork.com/freelancers/~01eaecb2fca73ffc2a
- **Email**: sanoel56@gmail.com

## License

MIT — free to use and modify. Attribution appreciated but not required.
