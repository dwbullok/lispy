(defmacro defun (name params &rest body)
    `(progn
     (setf (symbol-function ',name)
    #'(lambda ,params
    (block ,name ,@body)))
    ',name))