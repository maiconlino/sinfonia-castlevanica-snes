; Original fixed-size long conditional branch macros.
.macro jeq target
 bne *+5
 jmp target
.endmacro
.macro jne target
 beq *+5
 jmp target
.endmacro
.macro jcs target
 bcc *+5
 jmp target
.endmacro
.macro jcc target
 bcs *+5
 jmp target
.endmacro
.macro jmi target
 bpl *+5
 jmp target
.endmacro
.macro jpl target
 bmi *+5
 jmp target
.endmacro
.macro jvs target
 bvc *+5
 jmp target
.endmacro
.macro jvc target
 bvs *+5
 jmp target
.endmacro
