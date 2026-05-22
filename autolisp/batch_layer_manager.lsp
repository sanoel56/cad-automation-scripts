(defun c:BATCHLAYER (/ *error* oldPrefix newPrefix layerList ss doc layers layerName newName)
  ;; Batch Layer Manager - Rename layers with prefix/suffix
  ;; Supports AutoCAD 2021+ and LT 2024+
  
  ;; Error handling function
  (defun *error* (msg)
    (if (not (member msg '("Function cancelled" "quit / exit abort")))
      (princ (strcat "\nError: " msg))
    )
    (vla-endundomark doc)
    (princ)
  )

  ;; Start undo mark
  (setq doc (vla-get-activedocument (vlax-get-acad-object)))
  (vla-startundomark doc)

  ;; Prompt user for prefix to add
  (setq oldPrefix (getstring T "\nEnter prefix to add to all layer names: "))
  (if (= oldPrefix "")
    (progn
      (princ "\nNo prefix entered. Operation cancelled.")
      (vla-endundomark doc)
      (exit)
    )
  )

  ;; Get all layers in the drawing
  (setq layerList (vla-get-layers doc))
  (setq layerCount 0)

  ;; Iterate through each layer
  (vlax-for layer layerList
    (setq layerName (vla-get-name layer))
    ;; Skip special layers that cannot be renamed
    (if (not (wcmatch layerName "*|*"))  ;; Skip xref-dependent layers
      (progn
        ;; Check if layer already has the prefix
        (if (not (wcmatch layerName (strcat oldPrefix "*")))
          (progn
            ;; Rename the layer
            (setq newName (strcat oldPrefix layerName))
            (if (vl-catch-all-error-p
                  (vl-catch-all-apply 'vla-put-name (list layer newName)))
              (princ (strcat "\nCould not rename layer: " layerName))
              (progn
                (setq layerCount (1+ layerCount))
                (princ (strcat "\nRenamed: " layerName " -> " newName))
              )
            )
          )
        )
      )
    )
  )

  ;; Display summary
  (princ (strcat "\n\nTotal layers renamed: " (itoa layerCount)))
  (vla-endundomark doc)
  (princ)
)