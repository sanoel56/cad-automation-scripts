# How to Load and Run AutoLISP Scripts in AutoCAD

## Step 1: Download the script
Save the `.lsp` file anywhere on your computer.

## Step 2: Load into AutoCAD
1. Open AutoCAD
2. Type `APPLOAD` and press Enter
3. Browse to the `.lsp` file → select it → click **Load**
4. You should see "Type [COMMAND] to run" in the command line
5. Click **Close**

For automatic loading every time AutoCAD starts:
1. In the APPLOAD dialog, click **Contents** under Startup Suite
2. Click **Add** → select the `.lsp` file
3. Click **Close** on all dialogs

## Step 3: Run the script
Type the command name shown in each script's documentation and press Enter.

## Compatibility
- AutoCAD 2021+ (Windows and Mac)
- AutoCAD LT 2024+ (partial support)
- BricsCAD, ZWCAD, and other AutoCAD-compatible CAD platforms
