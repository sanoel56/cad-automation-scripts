(defun c:ANNO (/ *error* ss obj objType scales scaleList i j)
  ;; Auto-set annotative scales for text, dimensions, blocks
  ;; Command: ANNO
  ;; Select objects to update, then specify scales

  ;; Error handling function
  (defun *error* (msg)
    (if (not (wcmatch (strcase msg t) "*break*,*cancel*,*exit*"))
      (princ (strcat "\nError: " msg))
    )
    (princ)
  )

  ;; Prompt user to select objects
  (princ "\nSelect annotative objects (text, dimensions, blocks) to set scales: ")
  (setq ss (ssget '((0 . "TEXT,MTEXT,DIMENSION,INSERT"))))
  (if (not ss)
    (progn
      (princ "\nNo objects selected or selection cancelled.")
      (exit)
    )
  )

  ;; Prompt user for scales
  (princ "\nEnter annotative scales (comma-separated, e.g. 1:100,1:50,1:200): ")
  (setq scaleList (getstring t))
  (if (= scaleList "")
    (progn
      (princ "\nNo scales entered. Exiting.")
      (exit)
    )
  )

  ;; Parse scales into list
  (setq scales (mapcar 'strcase (mapcar 'vl-string-trim " " (LM:str->lst scaleList ","))))

  ;; Process each selected object
  (setq i 0)
  (repeat (sslength ss)
    (setq obj (vlax-ename->vla-object (ssname ss i)))
    (setq objType (vla-get-ObjectName obj))

    ;; Check if object supports annotative scales
    (if (and (vlax-property-available-p obj 'Annotative)
             (vlax-get obj 'Annotative))
      (progn
        ;; Clear existing scales
        (vlax-invoke obj 'DeleteAnnotationScales)
        ;; Add each scale
        (setq j 0)
        (repeat (length scales)
          (vlax-invoke obj 'AddAnnotationScale (nth j scales))
          (setq j (1+ j))
        )
        (princ (strcat "\nUpdated object " (itoa (1+ i)) ": " objType))
      )
      (princ (strcat "\nObject " (itoa (1+ i)) " is not annotative or does not support scales."))
    )
    (setq i (1+ i))
  )

  (princ (strcat "\nProcessed " (itoa i) " objects."))
  (princ)
)

;; Helper function to convert string to list by delimiter
(defun LM:str->lst (str del / pos lst)
  (if (and str del)
    (progn
      (while (setq pos (vl-string-search del str))
        (setq lst (cons (substr str 1 pos) lst)
              str (substr str (+ pos 1 (strlen del)))
        )
      )
      (reverse (cons str lst))
    )
  )
)

;; Load and run
(princ "\nAnnotation Scale Setter loaded. Type ANNO to run.")
(princ)
