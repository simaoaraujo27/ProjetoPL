      PROGRAM MOSTRADOBRO
      INTEGER X
      PRINT *, 'Introduza um inteiro:'
      READ *, X
      CALL ESCREVEDOBRO(X)
      END

      SUBROUTINE ESCREVEDOBRO(A)
      INTEGER A, R
      R = A + A
      PRINT *, 'Dobro = ', R
      RETURN
      END
