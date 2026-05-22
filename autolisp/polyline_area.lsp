(defun c:POLYAREA (/ *error* ss i ent obj area len total_area total_len data_list) (vl-load-com)

  ;; Error handling function
  (defun *error* (msg)
    (if (not (wcmatch (strcase msg t) "*break,*cancel*,*exit*"))
      (princ (strcat "\nError: " msg))
    )
    (princ)
  )

  ;; Initialize totals
  (setq total_area 0.0 total_len 0.0 data_list '())

  ;; Prompt user to select polylines
  (princ "\nSelect polylines to calculate area and length...")
  (setq ss (ssget '((0 . "LWPOLYLINE,POLYLINE"))))

  (if (not ss)
    (progn
      (princ "\nNo polylines selected.")
      (exit)
    )
  )

  ;; Process each polyline
  (setq i 0)
  (repeat (sslength ss)
    (setq ent (ssname ss i)
          obj (vlax-ename->vla-object ent)
    )
    (if (and obj
             (or (= (vla-get-ObjectName obj) "AcDbPolyline")
                 (= (vla-get-ObjectName obj) "AcDb2dPolyline")
                 (= (vla-get-ObjectName obj) "AcDb3dPolyline")
             )
        )
      (progn
        ;; Get area (if closed) or length
        (if (vlax-property-available-p obj 'Area)
          (setq area (vla-get-Area obj))
          (setq area 0.0)
        )
        (setq len (vla-get-Length obj))
        (setq total_area (+ total_area area)
              total_len (+ total_len len)
        )
        ;; Store data for table
        (setq data_list (cons (list (1+ i) area len) data_list))
      )
    )
    (setq i (1+ i))
  )

  ;; Reverse list to maintain original order
  (setq data_list (reverse data_list))

  ;; Create table in drawing
  (if (not (tblsearch "STYLE" "Standard"))
    (command "_.STYLE" "Standard" "txt.shx" 0.0 1.0 0.0 "N" "N" "N")
  )

  (command "_.TABLE")
  (while (> (getvar 'cmdactive) 0)
    (command "_")
  )

  ;; Get the last created table
  (setq table_ent (entlast))
  (if (and table_ent
           (= (cdr (assoc 0 (entget table_ent))) "ACAD_TABLE")
      )
    (progn
      ;; Set table properties
      (setq table_obj (vlax-ename->vla-object table_ent))
      (vla-put-TitleSuppressed table_obj :vlax-false)
      (vla-put-HeaderSuppressed table_obj :vlax-false)

      ;; Set number of rows and columns
      (vla-SetSize table_obj (1+ (length data_list)) 3)

      ;; Set column widths
      (vla-SetColumnWidth table_obj 0 50)
      (vla-SetColumnWidth table_obj 1 100)
      (vla-SetColumnWidth table_obj 2 100)

      ;; Set row heights
      (vla-SetRowHeight table_obj 0 15)
      (vla-SetRowHeight table_obj 1 15)

      ;; Fill header row
      (vla-SetText table_obj 0 0 "No.")
      (vla-SetText table_obj 0 1 "Area (sq. units)")
      (vla-SetText table_obj 0 2 "Length (units)")

      ;; Fill data rows
      (setq row 1)
      (foreach item data_list
        (vla-SetText table_obj row 0 (itoa (car item)))
        (vla-SetText table_obj row 1 (rtos (cadr item) 2 2))
        (vla-SetText table_obj row 2 (rtos (caddr item) 2 2))
        (setq row (1+ row))
      )

      ;; Add totals row
      (vla-SetText table_obj row 0 "Total")
      (vla-SetText table_obj row 1 (rtos total_area 2 2))
      (vla-SetText table_obj row 2 (rtos total_len 2 2))

      ;; Update table
      (vla-Update table_obj)
    )
  )

  ;; Print summary to command line
  (princ (strcat "\nTotal polylines processed: " (itoa (sslength ss))))
  (princ (strcat "\nTotal area: " (rtos total_area 2 2) " sq. units"))
  (princ (strcat "\nTotal length: " (rtos total_len 2 2) " units"))

  (princ)
)

(princ "\nPOLYAREA loaded. Type POLYAREA to run.")
(princ)
