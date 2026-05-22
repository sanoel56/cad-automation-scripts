(defun c:ATTREDIT (/ *error* ss i blk att attlist newval oldval tag)
  ;; Error handling function
  (defun *error* (msg)
    (if (not (wcmatch (strcase msg t) "*break*,*cancel*,*exit*"))
      (princ (strcat "\nError: " msg))
    )
    (princ)
  )

  ;; Main function
  (princ "\nSelect blocks with attributes to edit...")
  (setq ss (ssget '((0 . "INSERT") (66 . 1))))  ; Filter for blocks with attributes
  (if (not ss)
    (progn
      (princ "\nNo blocks with attributes selected.")
      (exit)
    )
  )

  ;; Extract attribute tags from first block
  (setq i 0)
  (setq blk (ssname ss i))
  (setq att (entnext blk))
  (setq attlist '())
  (while (and att (= (cdr (assoc 0 (entget att))) "ATTRIB"))
    (setq tag (cdr (assoc 2 (entget att))))
    (setq attlist (cons tag attlist))
    (setq att (entnext att))
  )
  (setq attlist (reverse attlist))

  ;; Display tags and let user choose
  (princ "\nAvailable attribute tags:")
  (foreach tag attlist
    (princ (strcat "\n  " tag))
  )
  (setq tag (getstring t "\nEnter tag to edit (or press Enter to cancel): "))
  (if (= tag "")
    (progn
      (princ "\nOperation cancelled.")
      (exit)
    )
  )

  ;; Get new value
  (setq newval (getstring t (strcat "\nEnter new value for \"" tag "\": ")))
  (if (= newval "")
    (progn
      (princ "\nOperation cancelled.")
      (exit)
    )
  )

  ;; Update all selected blocks
  (setq i 0)
  (repeat (sslength ss)
    (setq blk (ssname ss i))
    (setq att (entnext blk))
    (while (and att (= (cdr (assoc 0 (entget att))) "ATTRIB"))
      (if (= (cdr (assoc 2 (entget att))) tag)
        (progn
          (setq oldval (cdr (assoc 1 (entget att))))
          (setq attdata (entget att))
          (setq attdata (subst (cons 1 newval) (assoc 1 attdata) attdata))
          (entmod attdata)
          (entupd blk)
          (princ (strcat "\nUpdated block " (itoa (1+ i)) ": \"" oldval "\" -> \"" newval "\""))
        )
      )
      (setq att (entnext att))
    )
    (setq i (1+ i))
  )

  (princ (strcat "\nDone. Updated " (itoa i) " blocks."))
  (princ)
)