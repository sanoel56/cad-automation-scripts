(defun c:EXPC (/ *error* ss i ent pt coord-list file-path file) ; Export Point Coordinates to CSV
  ; Define error handler
  (defun *error* (msg)
    (if file (close file))
    (if (and msg (not (wcmatch (strcase msg) "*BREAK*,*CANCEL*,*EXIT*")))
      (princ (strcat "\nError: " msg))
    )
    (princ)
  )

  ; Prompt user to select point objects
  (princ "\nSelect point objects to export coordinates...")
  (setq ss (ssget '((0 . "POINT"))))
  (if (not ss)
    (progn
      (princ "\nNo points selected or selection cancelled.")
      (exit)
    )
  )

  ; Get output file path
  (setq file-path (getfiled "Save CSV File" "" "csv" 1))
  (if (not file-path)
    (progn
      (princ "\nFile selection cancelled.")
      (exit)
    )
  )

  ; Open file for writing
  (setq file (open file-path "w"))
  (if (not file)
    (progn
      (princ (strcat "\nCannot open file: " file-path))
      (exit)
    )
  )

  ; Write CSV header
  (write-line "X,Y,Z" file)

  ; Process each selected point
  (setq i 0)
  (repeat (sslength ss)
    (setq ent (ssname ss i))
    (setq pt (cdr (assoc 10 (entget ent))))
    (setq coord-list (list (rtos (car pt) 2 6) (rtos (cadr pt) 2 6) (rtos (caddr pt) 2 6)))
    (write-line (strcat (nth 0 coord-list) "," (nth 1 coord-list) "," (nth 2 coord-list)) file)
    (setq i (1+ i))
  )

  ; Close file
  (close file)

  ; Report success
  (princ (strcat "\nExported " (itoa (sslength ss)) " point coordinates to " file-path))
  (princ)
)

(princ "\nEXPC command loaded. Type EXPC to run.")
(princ)
