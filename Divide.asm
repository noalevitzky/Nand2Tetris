@c
M=1
@R14
D=M
@b // retrieve the value of R14
M=D
@R13
D=M
@a
M=D // retrieve the value of R13
@R15
M=0


(LOOP1)
@b
D=M
@d
M=D //d=b
M=M<< //d=d<<
D=M //retrieve d=b<<
@a
D=D-M //d=a-b<<
@LOOP2
D;JGT // go to LOOP2 if b-a>0
@b
M=M<<
@c
M=M<<
@LOOP1
0;JEQ


(LOOP2)
@c
D=M
@END
D;JLE // exit loop if c<= 0
@b
D=M
@a
D=M-D // D=a-b
@CONDITION
D;JGE
@LOOP3
0;JEQ


(LOOP3)
@c
M=M>>
@b
M=M>>
@LOOP2
0;JEQ


(CONDITION)
@b
D=M
@a
M=M-D
@c
D=M
@R15
M=M+D
@LOOP3
0;JEQ

(END)
@END
0;JEQ



