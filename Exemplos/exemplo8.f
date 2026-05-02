      PROGRAM DECRESCENTE
      INTEGER N, I, S
      PRINT *, 'Introduza um inteiro positivo:'
      READ *, N
      S = 0
      DO 10 I = N, 1, -2
      S = S + I
   10 CONTINUE
      PRINT *, 'Soma decrescente = ', S
      END
