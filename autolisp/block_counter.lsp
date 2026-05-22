(defun c:BLKCNT (/ *error* ss i blkName blkCount blkList tbl csvFile csvPath)
  ;; Count blocks and export to table or CSV
  ;; Command: BLKCNT
  ;; Author: AutoLISP Expert
  ;; Version: 1.0
  ;; Compatibility: AutoCAD 2021+ / LT 2024+

  ;; Error handling function
  (defun *error* (msg)
    (if msg
      (princ (strcat "\nError: " msg))
    )
    (princ)
  )

  ;; Prompt user to select blocks or entire drawing
  (princ "\nSelect blocks to count (or press Enter for entire drawing): ")
  (setq ss (ssget '((0 . "INSERT"))))
  (if (null ss)
    (progn
      (princ "\nNo blocks selected. Counting all blocks in drawing...")
      (setq ss (ssget "_X" '((0 . "INSERT"))))
    )
  )

  (if (null ss)
    (progn
      (princ "\nNo blocks found in drawing.")
      (exit)
    )
  )

  ;; Initialize list to store block names and counts
  (setq blkList '())

  ;; Loop through selection set
  (setq i 0)
  (repeat (sslength ss)
    (setq blkName (cdr (assoc 2 (entget (ssname ss i)))))
    (setq blkCount (assoc blkName blkList))
    (if blkCount
      ;; Increment count if block already in list
      (setq blkList (subst (cons blkName (1+ (cdr blkCount))) blkCount blkList))
      ;; Add new block to list
      (setq blkList (cons (cons blkName 1) blkList))
    )
    (setq i (1+ i))
  )

  ;; Sort list by block name (optional)
  (setq blkList (vl-sort blkList '(lambda (a b) (< (car a) (car b)))))

  ;; Ask user for export method
  (initget "Table CSV")
  (setq choice (getkword "\nExport to [Table/CSV]? <Table>: "))
  (if (null choice) (setq choice "Table"))

  (cond
    ((= choice "Table")
      ;; Create table in drawing
      (setq tbl (vla-addtable
                  (vla-get-modelspace (vla-get-activedocument (vlax-get-acad-object)))
                  (vlax-3d-point (getpoint "\nPick insertion point for table: "))
                  (1+ (length blkList))  ;; rows (header + data)
                  2  ;; columns
                  nil nil
                )
      )
      ;; Set table title
      (vla-settext tbl 0 0 "Block Count")
      ;; Set column headers
      (vla-settext tbl 1 0 "Block Name")
      (vla-settext tbl 1 1 "Count")
      ;; Fill data
      (setq i 0)
      (foreach item blkList
        (vla-settext tbl (+ 2 i) 0 (car item))
        (vla-settext tbl (+ 2 i) 1 (itoa (cdr item)))
        (setq i (1+ i))
      )
      ;; Adjust column widths
      (vla-setcolumnwidth tbl 0 30)
      (vla-setcolumnwidth tbl 1 10)
      (princ "\nTable created successfully.")
    )
    ((= choice "CSV")
      ;; Export to CSV file
      (setq csvPath (getfiled "Save CSV file" "" "csv" 1))
      (if csvPath
        (progn
          (setq csvFile (open csvPath "w"))
          ;; Write header
          (write-line "Block Name,Count" csvFile)
          ;; Write data
          (foreach item blkList
            (write-line (strcat (car item) "," (itoa (cdr item))) csvFile)
          )
          (close csvFile)
          (princ (strcat "\nCSV file saved to: " csvPath))
        )
        (princ "\nExport cancelled.")
      )
    )
  )

  (princ)
)
