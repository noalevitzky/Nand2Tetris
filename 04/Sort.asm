// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Sort.asm

@i
M=-1

(LOOP0)
@i
M=M+1
@R15
D=M-1 //D = n-1
@i
D=D-M
@END
D;JEQ //if D==0 exit loop
@j
M=-1


(LOOP1)
@j
M=M+1
@R15
D=M-1
@i
D=D-M
@j
D=D-M // D=n-1-i-j
@LOOP0
D;JEQ //if D==0 exit loop


//get arr[j+1]
@R14
D=M
@j
D=D+M
D=D+1 //D is the (Arr[j+1])'s address
@rightAddress
M=D
A=D
D=M //D is Arr[j+1]
@right
M=D //M is Arr[j+1]

//get Arr[j]
@R14
D=M
@j
D=D+M //D is the (Arr[j])'s address
@leftAddress
M=D
A=D
D=M //D is Arr[j]
@left
M=D 
@right
D=D-M // D is (Arr[j]-Arr[j+1])

@SWAP
D;JLT //swap if Arr[j]<Arr[j+1]
@LOOP1
0;JMP

(SWAP)
@left
D=M
@temp
M=D //temp = Arr[j]
@right
D=M //D = Arr[j+1]
@leftAddress
A=M
M=D //Arr[j] = Arr[j+1]
@temp
D=M //D = Arr[j]
@rightAddress
A=M
M=D //Arr[j+1] = temp
@LOOP1
0;JMP


(END)
@END
0;JMP //Exit program, verify later
