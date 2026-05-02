      PROGRAM ESTADO
      INTEGER X
      LOGICAL OK
      PRINT *, 'Introduza um inteiro:'
      READ *, X
      OK = .NOT. (X .LT. 0)
      IF (OK .OR. X .EQ. -3) THEN
      PRINT *, 'Estado aceite'
      ELSE
      PRINT *, 'Estado rejeitado'
      ENDIF
      END
