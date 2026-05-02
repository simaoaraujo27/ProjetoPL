      PROGRAM TAB2D
      INTEGER M(1:2,5:7), V1, V2, X
      PRINT *, 'Introduza dois inteiros:'
      READ *, V1, V2
      M(1,5) = V1
      M(2,7) = V2
      X = M(1,5) + M(2,7)
      PRINT *, 'Soma = ', X
      END
