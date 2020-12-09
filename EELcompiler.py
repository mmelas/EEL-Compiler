
# coding: utf-8

# In[91]:


import sys
global lexout
global token

global lines
global cnt
global quads
global scopes
global nestingLevel
global offsetVal
global notSubProg  #flag gia thn paragwgh H oxi tou C kwdika
global mainFrameLength
global asmFile
global labelCnt
global procLabel


notSubProg = True
quads = []
scopes = []
cnt = 0
nestingLevel = -1
offsetVal = 12
mainFrameLength = 0
lines = {}
count = 1
lineNum = 1
en = 0
labelCnt = 0
procLabel = {}



# In[2]:


def gnlvcode(var):
    scope,offset,parMode = findDeclaration(var)
    asmFile.write('lw $t0,-4($sp)\n')
    for i in range(nestingLevel,scope+1,- 1):
        asmFile.write('lw $t0,-4($t0)\n')
    asmFile.write('add $t0,$t0,-'+ str(offset) +'\n')        

    


# In[3]:


def findDeclaration(name):  
    for i in range(nestingLevel,-1,-1):
        for j in range(len(scopes[i])):
            if(name == scopes[i][j][0] and len(scopes[i][j]) == 2):   #[name, offset]
                return i, scopes[i][j][1], None
            elif(name == scopes[i][j][0] and len(scopes[i][j]) == 3): #[name, offset, parMode]
                return i, scopes[i][j][1], scopes[i][j][2]
            elif(name == scopes[i][j][0] and len(scopes[i][j]) == 4): #[name,[...],startQuad,framelength]
                return -1,scopes[i][j][3], i
    print('error, variable/proc/func', name, ' is not defined')
    print('line',lineNum,':',lines[lineNum])
    exit()


# In[4]:


def removeLastScope():
    global nestingLevel
    global scopes
    scopes.pop(nestingLevel)
    nestingLevel -= 1


# In[5]:


def addScope():
    global nestingLevel
    global offsetVal
    global scopes
    scopes.append([])
    offsetVal = 12
    nestingLevel += 1


# In[6]:


def loadvr(v,r):
    global asmFile
    tr = '$t' + str(r)
    if( v.isdigit() or  v.lstrip('-').isdigit()):            #an einai stathera
        asmFile.write('li '+tr+','+v+'\n')
    else:
        scopeLvl, offset, parMode = findDeclaration(v)
        if(scopeLvl == 0):                              #an einai dhlwmneh sthn main
            asmFile.write('lw '+tr+',-'+str(offset)+'($s0)\n')
        elif scopeLvl==nestingLevel:                 #an einai dhlwmneh se AUTO to scope
            if(parMode == 'in' or parMode == None):   #"parmode = in" H "t.m. ara parmode = None" H "T_i"
                asmFile.write('lw '+tr+',-'+str(offset)+'($sp)\n')
            elif(parMode == 'inout'):          #"parmode = inout"
                asmFile.write('lw $t0,-'+str(offset)+'($sp)\n')
                asmFile.write('lw '+tr+',($t0)\n')
        else:                                         #an einai dhlwmneh se ALLO scope
            if(parMode == 'in' or parMode == None):   #"parmode = in" H "t.m. ara parmode = None"
                gnlvcode(v)
                asmFile.write('lw '+tr+',($t0)\n')
            elif(parMode == 'inout'):          #"parmode = inout"
                gnlvcode(v)
                asmFile.write('lw $t0,($t0)\n')
                asmFile.write('lw '+tr+',($t0)\n')


# In[7]:


def storerv(r,v):
    global asmFile
    tr = '$t' + str(r)
    scopeLvl, offset, parMode = findDeclaration(v)
    if(scopeLvl == 0):
        asmFile.write('sw '+tr+',-'+str(offset)+'($s0)\n')
    elif(scopeLvl == nestingLevel):
        if(parMode == 'in' or parMode == None or ('T_' in v)):
            asmFile.write('sw '+tr+',-'+str(offset)+'($sp)\n')
        elif(parMode == 'inout'):
            asmFile.write('lw $t0,-'+str(offset)+'($sp)\n')
            asmFile.write('sw '+tr+',($t0)\n')
    else:
        if(parMode == 'in' or parMode == None):
            gnlvcode(v)
            asmFile.write('sw '+tr+',($t0)\n')
        elif(parMode == 'inout'):
            gnlvcode(v)
            asmFile.write('lw $t0,($t0)\n')
            asmFile.write('sw '+tr+',($t0)\n')
            


# In[8]:


def toAsm(stQuad):
    global labelCnt
    parCnt = 0
    asmFile.write('L'+str(labelCnt)+':\n')
    procLabel[quads[stQuad][1]] = labelCnt
    labelCnt += 1
    if nestingLevel > 0:
        asmFile.write('sw $ra,($sp)\n' )
    elif nestingLevel == 0:        #main    
        asmFile.write('Lmain: \n')
        asmFile.write('add $sp,$sp,' + str(mainFrameLength) + '\n')
        asmFile.write('move $s0,$sp\n')
    
    for i in range(stQuad+1,len(quads)-1):  #to +-1 einai gia na MHN pernoume to begin kai to end_block
                                            #ta opoia ta diaxeirizomaste panw kai katw ap'to for antistoixa.
        if(quads[i][0] == '' or quads[i][0] == 'halt'):               
            asmFile.write('L'+str(labelCnt)+':\n')
        else:
            asmFile.write('L'+str(labelCnt)+': ')
        
        labelCnt += 1
        if(quads[i][0] == ':='):    
            loadvr(quads[i][1],1)
            storerv(1,quads[i][3])
    
        elif(quads[i][0] == '+'):
            loadvr(quads[i][1],1)
            loadvr(quads[i][2],2)
            asmFile.write('add $t1,$t1,$t2\n' )
            storerv(1,quads[i][3])
        elif(quads[i][0] == '-'):
            loadvr(quads[i][1],1)
            loadvr(quads[i][2],2)
            asmFile.write('sub $t1,$t1,$t2\n' )
            storerv(1,quads[i][3])
        elif(quads[i][0] == '*'):
            loadvr(quads[i][1],1)
            loadvr(quads[i][2],2)
            asmFile.write('mul $t1,$t1,$t2\n' )
            storerv(1,quads[i][3])
        elif(quads[i][0] == '/'):
            loadvr(quads[i][1],1)
            loadvr(quads[i][2],2)
            asmFile.write('div $t1,$t1,$t2\n' )
            storerv(1,quads[i][3])
        
        
        
        elif(quads[i][0] == '<'):
            loadvr(quads[i][1],1)
            loadvr(quads[i][2],2)
            asmFile.write('blt $t1,$t2,L'+str(quads[i][3]) + '\n' )
        elif(quads[i][0] == '<=' ):
            loadvr(quads[i][1],1)
            loadvr(quads[i][2],2)
            asmFile.write('ble $t1,$t2,L'+str(quads[i][3]) + '\n' )
        elif( quads[i][0] == '>' ):
            loadvr(quads[i][1],1)
            loadvr(quads[i][2],2)
            asmFile.write('bgt $t1,$t2,L'+str(quads[i][3]) + '\n' )
        elif(quads[i][0] == '>='):
            loadvr(quads[i][1],1)
            loadvr(quads[i][2],2)
            asmFile.write('bge $t1,$t2,L'+str(quads[i][3]) + '\n' )
        elif(quads[i][0] == '<>'):
            loadvr(quads[i][1],1)
            loadvr(quads[i][2],2)
            asmFile.write('bne $t1,$t2,L'+str(quads[i][3]) + '\n' )
        elif(quads[i][0] == '='):
            loadvr(quads[i][1],1)
            loadvr(quads[i][2],2)
            asmFile.write('beq $t1,$t2,L'+str(quads[i][3]) + '\n' )
            
     
        elif(quads[i][0] == 'jump'):
            asmFile.write('j L'+ str(quads[i][3]) + '\n' )
      
        elif(quads[i][0] == 'print'):
            asmFile.write('li $v0,1\n')
            loadvr(quads[i][1],1)
            asmFile.write('move $a0,$t1\n' )
            asmFile.write('syscall\n' )
        
        elif(quads[i][0] == 'input'):
            asmFile.write('li $v0,5\n')
            asmFile.write('syscall\n')
            asmFile.write('move $t1,$v0\n')
            storerv(1,quads[i][3])
                          
        elif(quads[i][0] == 'ret'):
            loadvr(quads[i][1],1)
            asmFile.write('lw $t0,-8($sp)\n')
            asmFile.write('sw $t1,($t0)\n')
        elif(quads[i][0] == 'ret'):
            loadvr(quads[i][1],1)
            asmFile.write('lw $t0,-8($sp)\n')
            asmFile.write('sw $t1,($t0)\n')
        elif(quads[i][0] == 'par'):
            if(parCnt == 0):
                for j in range (i,len(quads)):
                    if(quads[j][0] == 'call'):
                        typeOf, frameLength, nothing = findDeclaration(quads[j][1])
                        if(typeOf == -1):
                            asmFile.write('add $fp,$sp,'+ str(frameLength) +'\n')
                            break
            if(quads[i][2] == 'in'):
                loadvr(quads[i][1],0)
                asmFile.write('sw $t0,-' + str(12+4*parCnt) + '($fp)\n')
            elif(quads[i][2] == 'inout'):
                scope, offset, parMode = findDeclaration(quads[i][1])
                if scope == nestingLevel:
                    if parMode == 'in' or parMode == None:
                        asmFile.write('add $t0,$sp,-'+ str(offset) +'\n')
                        asmFile.write('sw $t0,-' + str(12+4*parCnt) + '($fp)\n')
                    elif parMode == 'inout':
                        asmFile.write('lw $t0,-'+ str(offset) +'($sp)\n')
                        asmFile.write('sw $t0,-' + str(12+4*parCnt) + '($fp)\n')
                elif scope != nestingLevel:
                    if parMode == 'in' or parMode == None:
                        gnlvcode(quads[i][1])
                        asmFile.write('sw $t0,-' + str(12+4*parCnt) + '($fp)\n')
                    elif parMode == 'inout':
                        gnlvcode(quads[i][1])
                        asmFile.write('lw $t0,($t0)\n')
                        asmFile.write('sw $t0,-' + str(12+4*parCnt) + '($fp)\n')
            elif(quads[i][2] == 'ret'):
                scope , offset, nothing = findDeclaration(quads[i][1])
                asmFile.write('add $t0,$sp,-'+ str(offset) +'\n')
                asmFile.write('sw $t0,-8($fp)\n')
            parCnt += 1
        elif(quads[i][0] == 'call'):
            parCnt = 0
            typeOf, frameLength, scope = findDeclaration(quads[i][1])
            if(scope == nestingLevel):
                asmFile.write('lw $t0,-4($sp)\n')
                asmFile.write('sw $t0,-4($fp)\n')
            elif(scope != nestingLevel):
                asmFile.write('sw $sp,-4($fp)\n')
            asmFile.write('add $sp,$sp,'+ str(frameLength) +'\n')
            asmFile.write('jal L' + str(procLabel[quads[i][1]]) + '\n')
            asmFile.write('add $sp,$sp,-'+ str(frameLength) +'\n')
    
    asmFile.write('L'+str(labelCnt)+':\n')
    labelCnt += 1
    if nestingLevel > 0:
        asmFile.write('lw $ra,($sp)\n')
        asmFile.write('jr $ra\n')
            


# In[9]:


def lex():
    global lineNum
    global en
    global nextChar
    global lastChar
    if(en == 0):
        nextChar = file.read(1)   
    else:
        nextChar = lastChar
    lastChar = state_0(nextChar)


# In[68]:


def state_0(nextChar):
    global en
    global lineNum
    global lexout
    global token
    en = 0
    endOfComm = True
    while nextChar == " " or nextChar == "\t" or nextChar == "\n":
        if(nextChar == '\n'):
            lineNum += 1
        nextChar = file.read(1)
    if(nextChar.isalpha()):
        en = 1
        return (state_1(nextChar))
    elif(nextChar.isdigit()):
        en = 1
        return (state_2(nextChar))
    elif(nextChar == '+'):
        lexout = '+'
        token = 'plustk'
        return()
    elif(nextChar == '-'):
        lexout = '-'
        token = 'minustk'
        return()
    elif(nextChar == '*'):
        lexout = '*'
        token = 'multk'
        return()
    elif(nextChar == '/'):
        nextChar = file.read(1)
        if(nextChar == '*'):
            lineOfCom = lineNum
            nextChar = file.read(1)
            while(endOfComm):
                if(nextChar == '\n'):
                    nextChar = file.read(1)
                    lineNum += 1
                elif(nextChar == '*'):
                    nextChar = file.read(1)
                    if(nextChar == '/'):
                        nextChar = file.read(1)
                        return(state_0(nextChar))
                        endOfComm = False
                elif(nextChar == ''):
                    print('EOF error - comment started at line',
                        lineOfCom,'and never closed until End Of File.')
                    print('line',lineOfCom,':',lines[lineOfCom])
                    exit()
                    #termatismos tou programmatos ara kai ths loupas
                else:
                    nextChar = file.read(1)
        elif(nextChar == '/'):
            nextChar = file.read(1)
            while(nextChar != '\n' and nextChar != ''):
                nextChar = file.read(1)
            return(state_0(nextChar))
        else:
            lexout = '/'
            token = 'divtk'
            en = 1
            return(nextChar)
        return()
    elif(nextChar == '='):
        lexout = '='
        token = 'equaltk'
        return()
    elif(nextChar == '<'):
        nextChar = file.read(1)
        if(nextChar == '>'):
            lexout = '<>'
            token = 'notequaltk'
            return()
        elif(nextChar == '='):
            lexout = '<='
            token = 'lessequaltk'
            return()
        else:
            lexout = '<'
            token = 'lesstk'
            en = 1
            return(nextChar)   
    elif(nextChar == '>'):
        nextChar = file.read(1)
        if(nextChar == '='):
            lexout = '>='
            token = 'greaterequaltk'
            return()
        else:
            lexout = '>'
            token = 'greatertk'
            en = 1
            return(nextChar)       
    elif(nextChar == ':'):
        nextChar = file.read(1)
        if(nextChar == '='):
            lexout = ':='
            token = 'assignmenttk'
            return()
        else:
            en = 1
            lexout = ':'
            token = 'colontk'
            return(nextChar)
    elif(nextChar == ','):
        lexout = ','
        token = 'commatk'
        return()
    elif(nextChar == ';'):
        lexout = ';'
        token = 'qmarktk'
        return()
    elif(nextChar == '('):
        lexout = '('
        token = 'openbrackettk'
        return()
    elif(nextChar == ')'):
        lexout = ')'
        token = 'closebrackettk'
        return()
    elif(nextChar == ''):
        #EOF
        lexout = ''
        token = ''
        return('EOF')
    elif(nextChar == '['):
        lexout = '['
        token = 'opensquarebrackettk'
        return()
    elif(nextChar == ']'):
        lexout = ']'
        token = 'closesquarebrackettk'
        return()
    else:
        #error
        print('wrong character',nextChar,' at line:',lineNum)
        print('line',lineNum,':',lines[lineNum])
        exit()


# In[69]:


def state_1(nextChar):
    global lexout
    global token
    count = 0
    strToken = ''
    tks = ['program','endprogram','declare','enddeclare','if','then','else',
           'endif','while','endwhile','repeat','endrepeat','exit',
           'switch','case','endswitch','forcase','when','endforcase','procedure',
          'endprocedure','function','endfunction','call','return','in',
           'inout','and','or', 'not','true','false','input','print']
     
    while(nextChar.isalpha() or nextChar.isdigit()):
        if(count < 30):
            strToken += nextChar
        count += 1
        nextChar = file.read(1)
    
    token = 'idtk' #an den einai sth lista afou einai alfarithmitiko tha nai idtk
    if(strToken in tks):
        token = strToken+'tk'
    lexout = strToken
    return(nextChar)


# In[70]:


def state_2(nextChar):
    global lexout
    global token
    constToken = ""
    while(nextChar.isdigit()):
        constToken += nextChar
        nextChar = file.read(1)
    token = 'consttk'
    lexout = constToken
    if(int(lexout) > 32767):
        print('Variable out ouf bounds. Expected number between -32767 and 32767 but number'
            ,lexout,',line',lineNum)
        print('line',lineNum,':',lines[lineNum])
        exit()
    return(nextChar)


# In[71]:


def main():
    global token
    lex()
    program()


# In[72]:


def program():
    global token
    if token == 'programtk':
        lex()
        if token == 'idtk':
            addScope()
            name = lexout
            lineOfProgram = lineNum
            lex()
            block(name,1)  # 1 : programBlock
            if token == 'endprogramtk':
                removeLastScope()
                lineOfEnd = lineNum
                lex()
                if token != '':
                    print('End of program found at line'
                        ,lineOfEnd,'but there is code below it')
                    print('line',lineOfEnd,':',lines[lineOfEnd])
                    exit()

            else:
                print('Found program at line',lineOfProgram,'but endprogram not found')
                print('line',lineOfProgram,':',lines[lineOfProgram])
                exit()

        else:
            print('Expected Id for program at line:', lineNum)
            print('line',lineNum,':',lines[lineNum])
            exit()

    else:
        print('Start of program not found')
        print('line',lineNum,':',lines[lineNum])
        exit()


# In[73]:


def block(name,typeOfBlock):
    global offsetVal
    global mainFrameLength
    foundRet = False
    declarations()
    buffLastOf = offsetVal
    subprograms()
    if(nestingLevel >= 1):
        scopes[nestingLevel-1][ len(scopes[nestingLevel-1]) - 1 ].append(nextQuad())
    startQ = nextQuad()
    genQuad('begin_block',name,'','')
    tempOffset = offsetVal
    offsetVal = buffLastOf
    statements()
    if(nestingLevel >= 1):
        scopes[nestingLevel-1][len(scopes[nestingLevel-1])-1].append(offsetVal)
    else:
        mainFrameLength = offsetVal
    offsetVal =  tempOffset
    # typeOfBlock = 1 for main program / typeOfBlock = 2 for proc / typeOfBlock = 3 for func
    # Only for main program:
    if(typeOfBlock == 1):  
        genQuad('halt','','','')
    elif(typeOfBlock == 2):
        for i in range(startQ,len(quads)):
            if(quads[i][0] == 'ret'):
                print('Found return in procedure ' + quads[startQ][1] + '. Return is only allowed in function.')
              #  exit()
    elif(typeOfBlock == 3):
        for i in range(startQ,len(quads)):
            if(quads[i][0] == 'ret'):
                foundRet = True
        if(foundRet == False):
            print('Return not found in function ' + quads[startQ][1] + '. ALL functions must return a value')
            exit()
    genQuad('end_block',name,'','')
    toAsm(startQ)
   


# In[74]:



def declarations():
    global token
    global offsetVal
    if token == 'declaretk':
        lineOfDec = lineNum
        lex()
        varlist()
        if token == 'enddeclaretk':
            lex()
        else:
            print('Started declare at line',lineOfDec,'but enddeclare not found')
            print('line',lineOfDec,':',lines[lineOfDec])
            exit()


# In[75]:


def varlist():
    global offsetVal
    tempIdList = []
    if token == 'idtk':
        scopes[nestingLevel].append([lexout,offsetVal])
        offsetVal += 4
        tempIdList.append(lexout)
        lex()
        while token == 'commatk':
            lex()
            if(token == 'idtk'):
                if(lexout in tempIdList):
                    print('The variable ',lexout,' all ready exists in line ',lineNum)
                    print('line',lineNum,':',lines[lineNum])
                    exit()
                tempIdList.append(lexout)
              
                scopes[nestingLevel].append([lexout,offsetVal])
                offsetVal += 4
                lex()
                if(token != 'enddeclaretk' and token != 'commatk'):
                    print('Expected comma "," after variable at line',lineNum)
                    print('line',lineNum,':',lines[lineNum])
                    exit()
            else:
                print('variable not found after comma (",") in declarations at line :',lineNum)
                print('line',lineNum,':',lines[lineNum])
                exit()


# In[76]:


def subprograms():
    global notSubProg
    while(token == 'proceduretk' or token == 'functiontk'):
        notSubProg = False  #Flag to stop extract in .c for this file
        procorfunc()


# In[77]:


def procorfunc():
    if(token == 'proceduretk'):
        lineOfProc = lineNum
        lex()
        if(token == 'idtk'):
            addScope()
            name = lexout
            lex()
            procorfuncbody(name,2) #passing the name and the type : procedure
            if(token == 'endproceduretk'):
                removeLastScope()  
                lex()
            else:
                print('Started procedure at line',lineOfProc,'but endprocedure not found')
                print('line',lineOfProc,':',lines[lineOfProc])
                exit()
        else:
            print('id not found after procedure declaration at line',lineOfProc)
            print('line',lineOfProc,':',lines[lineOfProc])
            exit()

    elif(token == 'functiontk'):
        lineOfFunc = lineNum
        lex()
        if(token == 'idtk'):
            addScope()
            name = lexout
            lex()
            procorfuncbody(name,3) #passing the name and the type : function
            if(token == 'endfunctiontk'):
                removeLastScope()  
                lex()
            else:
                print('Started procedure at line',lineOfFunc,'but endprocedure not found')
                print('line',lineOfFunc,':',lines[lineOfFunc])
                exit()
        else:
            print('variable not found after function declaration at line',lineOfFunc)
            print('line',lineOfFunc,':',lines[lineOfFunc])
            exit()


# In[78]:


def procorfuncbody(name,typeOf):
    global nestingLevel
    scopes[nestingLevel-1].append([name])
    formalpars()
    
    block(name,typeOf)



# In[79]:


def formalpars():
    if(token == 'openbrackettk'):
        lineOfBrack = lineNum
        lex()
        formalparlist()
        if(token == 'closebrackettk'):
            lex()
        else:
            print('Found open parenthesis "(" at line',lineOfBrack,'but close parenthesis ")" not found')
            print('line',lineOfBrack,':',lines[lineOfBrack])
            exit()
    else:
        print('Expected open parenthesis "(" at line',lineNum)
        print('line',lineNum,':',lines[lineNum])
        exit()


# In[80]:


def formalparlist():
    scopes[nestingLevel-1][ len(scopes[nestingLevel-1]) - 1 ].append([])
    
    formalparitem()
    while token == 'commatk':
        lineOfComma = lineNum
        lex()
        if(token == 'intk' or token == 'inouttk'):
            formalparitem()
        else:
            print('Expected in/inout after "," at line',lineOfComma)
            print('line',lineOfComma,':',lines[lineOfComma])
            exit()


# In[81]:


def formalparitem():
    global offsetVal
    if token == 'intk' or token == 'inouttk':
        refBuffer = lexout
        scopes[nestingLevel-1][ len(scopes[nestingLevel-1]) - 1 ][1].append(lexout)
        lex()
        if token == 'idtk':
            scopes[nestingLevel].append([lexout,offsetVal,refBuffer])
            offsetVal += 4
            lex()
        else:
            print('Expected variable after in/inout at line',lineNum)
            print('line',lineNum,':',lines[lineNum])
            exit()


# In[82]:


def statements():
    exitList = []
    if(token == 'exittk'):
        exitList = makeList(nextQuad())
        genQuad('jump','','','')
    exitList3 = statement()
    exitList = merge(exitList,exitList3)
    while token == 'qmarktk':
        lex()
        if (token == 'idtk' or token == 'iftk'
         or token == 'whiletk' or token == 'exittk'
         or token == 'switchtk' or token == 'failuretk' 
         or token == 'calltk' or token == 'returntk'
         or token == 'printtk' or token == 'inputtk' 
         or token == 'repeattk' or token == 'forcasetk'):
            if(token == 'exittk'):
                exitList2 = makeList(nextQuad())
                genQuad('jump','','','')
                exitList = merge(exitList,exitList2)
            exitList3 = statement()
            exitList = merge(exitList,exitList3)
    if (token == 'idtk' or token == 'iftk'
         or token == 'whiletk' or token == 'exittk'
         or token == 'switchtk' or token == 'failuretk'
         or token == 'calltk' or token == 'returntk'
         or token == 'printtk' or token == 'inputtk' or token == 'repeattk' or token == 'forcasetk'):
        print('expected ";" between statements at line',lineNum)
        print('line',lineNum,':',lines[lineNum])
        exit()
    return(exitList)


# In[83]:


def statement():
    if(token == 'idtk'):
        assignmentStat()
    elif(token == 'iftk'):
        return ifStat()
    elif(token == 'whiletk'):
        return whileStat()
    elif(token == 'exittk'):
        exitStat()
    elif(token == 'switchtk'):
        return switchStat()
    #failureStat()
    elif(token == 'calltk'):
        callStat()
    elif(token == 'forcasetk'):
        return forCaseStat()
    elif(token == 'returntk'):
        returnStat()
    elif(token == 'repeattk'):
        repeatStat()
    elif(token == 'printtk'):
        printStat()
    elif(token == 'inputtk'):
        inputStat() 


# In[84]:


def assignmentStat():
    if(token == 'idtk'):
        var = lexout
        lex()
        if(token == 'assignmenttk'):
            lex()
            output = expression()
            genQuad(':=',output,'',var)
            return output
        else:
            print('expression expected after ":=" at line',lineNum)
            print('line',lineNum,':',lines[lineNum])
            exit()


# In[85]:


def ifStat():
    if(token == 'iftk'):
        lineOfIf = lineNum
        lex()
        bTrue,bFalse = condition()
        if(token == 'thentk'):
            backpatch(bTrue,nextQuad())
            lex()
            exitList = statements()
            ifList = makeList(nextQuad())
            genQuad('jump','','','')
            backpatch(bFalse,nextQuad())
            exitList2 = elsePart()
            exitList = merge(exitList,exitList2)
            backpatch(ifList,nextQuad())
            if(token == 'endiftk'):
                lex()
            else:
                print('Found if statement at line',lineOfIf,'but endif not found')
                print('line',lineOfIf,':',lines[lineOfIf])
                exit()
        else:
            print('Expected "then" after if statement at line',lineOfIf)
            print('line',lineOfIf,':',lines[lineOfIf])
            exit()
        return(exitList)


# In[86]:


def elsePart():
    if(token == 'elsetk'):
        lex()
        exitList = statements()
        return(exitList)
        #pou tha ginei to epomeno lex?  ---> mesa sto statement pou tha vrei


# In[29]:


def repeatStat():
    if(token == 'repeattk'):
        sQuad = nextQuad()
        lineOfRep = lineNum
        lex()
        exitList = statements()
        if(token == 'endrepeattk'):
            genQuad('jump','','',sQuad)
            backpatch(exitList,nextQuad())
            lex()
        else:
            print('Found repeat statement at line',lineOfRep,'but endrepeat not found',)
            print('line',lineOfRep,':',lines[lineOfRep])
            exit()


# In[30]:


def exitStat():
    if(token == 'exittk'):
        lex()


# In[31]:


def whileStat():
    if(token == 'whiletk'):
        bQuad = nextQuad()
        lineOfWhile = lineNum
        lex()
        bTrue,bFalse = condition()
        backpatch(bTrue,nextQuad())
        exitList = statements()
        genQuad('jump','','',bQuad)
        backpatch(bFalse,nextQuad())
        if(token == 'endwhiletk'):
            lex()
        else:
            print('Found while statement at line',lineOfWhile,'but endwhile not found',)
            print('line',lineOfWhile,':',lines[lineOfWhile])
            exit()
        return(exitList)


# In[32]:


def switchStat():
    if(token == 'switchtk'):
        lineOfSwitch = lineNum
        lex()
        ePlace1 = expression()
        if(token == 'casetk'):
            lineOfCase = lineNum
            lex()
            ePlace2 = expression()
            if(token == 'colontk'):
                switchTrueList = makeList(nextQuad())
                genQuad('=',ePlace1,ePlace2,'')
                switchFalseList = makeList(nextQuad())
                genQuad('jump','','','')
                backpatch(switchTrueList,nextQuad())
                lex()
                exitList = statements()
               
                switchList = makeList(nextQuad())
                genQuad('jump','','','')
                backpatch(switchFalseList,nextQuad())
            else:
                print('Expected ":" after expression in case at line',lineOfCase)
                print('line',lineOfCase,':',lines[lineOfCase])
                exit()
        else:
            print('At least one case needed for switch at line',lineOfSwitch)
            print('line',lineOfSwitch,':',lines[lineOfSwitch])
            exit()
        while(token == 'casetk'):
            lineOfCase = lineNum
            lex()
            ePlace2 = expression()
            if(token == 'colontk'):
                switchTrueList = makeList(nextQuad())
                genQuad('=',ePlace1,ePlace2,'')
                switchFalseList = makeList(nextQuad())
                genQuad('jump','','','')
                backpatch(switchTrueList,nextQuad())
                lex()
                exitList2 = statements()
               
                switchList2 = makeList(nextQuad())
                genQuad('jump','','','')
                backpatch(switchFalseList,nextQuad())
                switchList = merge(switchList,switchList2)
                
                exitList = merge(exitList,exitList2)
            else: 
                print('Expected ":" after expression in case at line',lineOfCase)
                print('line',lineOfCase,':',lines[lineOfCase])
                exit()
        if(token == 'endswitchtk'):
            backpatch(switchList,nextQuad())
            lex()
        else:
            print('Found switch statement at line',lineOfSwitch,'but endswitch not found')
            print('line',lineOfSwitch,':',lines[lineOfSwitch])
            exit()
        return(exitList)


# In[33]:


def forCaseStat():
    if(token == 'forcasetk'):
        flagFor = newTemp() 
        forLabel = nextQuad()
        genQuad(':=','0','',flagFor)
        lineOfFor = lineNum
        lex()
        if(token == 'whentk'):
            lineOfWhen = lineNum
            lex()
            qTrue,qFalse = condition()
            if(token == 'colontk'):
                backpatch(qTrue,nextQuad())
                lex()
                exitList = statements()
                genQuad(':=','1','',flagFor)
                backpatch(qFalse,nextQuad())
            else:
                print('Expected ":" after condition in for statement at line',lineNum)
                print('line',lineOfWhen,':',lines[lineOfWhen])
                exit()
        else:
            print('At least one when needed for forcase at line',lineOfFor)
            print('line',lineOfFor,':',lines[lineOfFor])
            exit()
        while(token == 'whentk'):
            lineOfWhen = lineNum
            lex()
            qTrue,qFalse = condition()
            if(token == 'colontk'):
                backpatch(qTrue,nextQuad())
                lex()
                exitList2 = statements()
                exitList = merge(exitList,exitList2)
                genQuad(':=','1','',flagFor)
                backpatch(qFalse,nextQuad())
            else:
                print('Expected ":" after condition in for statement at line',lineNum)
                print('line',lineOfWhen,':',lines[lineOfWhen])
                exit()
        if(token == 'endforcasetk'):  
            genQuad('=',flagFor,'1',forLabel)
            lex()
        else:
            print('Found forcase statement at line',lineOfFor,'but endforcase not found')
            print('line',lineOfFor,':',lines[lineOfFor])
            exit()
        return(exitList)


# In[34]:


def callStat():
    out = []
    if(token == 'calltk'):
        lex()
        if(token == 'idtk'):
            idCall = lexout
            lex()
            if(token == 'openbrackettk'):
                out = actualPars()
                if out is not None:
                    for i in range(len(out)):
                        genQuad('par',out[i][0],out[i][1],'')
                    genQuad('call',idCall,'','')
            else:
                print('Expected ( after id in call statement at line', lineNum)
                print('line',lineNum,':',lines[lineNum])
                exit()
                
        else:
            print('Expected function after call statement at line', lineNum)
            print('line',lineNum,':',lines[lineNum])
            exit()


# In[35]:


def actualPars():
    out = []
    if(token == 'openbrackettk'):
        lineOfBrack = lineNum
        lex()
        out = actualParList()
        if(token == 'closebrackettk'):
            lex()
        else:
            print('Found open parenthesis "(" at line',lineOfBrack,'but close parenthesis ")" not found')
            print('line',lineOfBrack,':',lines[lineOfBrack])
            exit()
        return out
    else:
        return 


# In[36]:


def actualParList():
    outInputs = []
    if(token != 'closebrackettk'):
        outInputs.append(actualParItem())
        while(token == 'commatk'):
            lex()
            outInputs.append(actualParItem())
    return outInputs


# In[37]:


def actualParItem():
    if(token == 'intk'):
        lex()
        term = expression()
        return [term,'in']
    elif(token == 'inouttk'):
        lex()
        if(token == 'idtk'):
            term = lexout
            lex()
            return [term,'inout']
        else:
            print('Expected variable after "inout" at line',lineNum)
            print('line',lineNum,':',lines[lineNum])
            exit()
    else:
        print('Expected in/inout expression after "," at line',lineNum)
        print('line',lineNum,':',lines[lineNum])
        exit()


# In[38]:


def returnStat():
    if(token == 'returntk'):
        lex()
        ePlace = expression()
        genQuad('ret',ePlace,'','')


# In[39]:


def condition():
    bTrue,bFalse = boolterm()
    while(token == 'ortk'):
        backpatch(bFalse,nextQuad())
        lex()
        q2True,q2False = boolterm()
        bTrue = merge(bTrue,q2True)
        bFalse = q2False
    return bTrue,bFalse


# In[40]:


def boolterm():
    r1True,r1False = boolfactor()
    qTrue,qFalse = r1True,r1False
    while(token == 'andtk'):
        backpatch(qTrue,nextQuad())
        lex()
        r2True,r2False = boolfactor()
        qFalse = merge(qFalse,r2False)
        qTrue = r2True
    return (qTrue,qFalse)


# In[41]:


def boolfactor():
    if(token == 'nottk'):
        lex()
        if(token == 'opensquarebrackettk'):
            lineOfBrack = lineNum
            lex()
            qFalse,qTrue = condition()
            if(token == 'closesquarebrackettk'):
                lex()
                return (qTrue,qFalse)
            else:
                print('Found open bracket "[" at line',lineOfBrack,'but close bracket "]" not found')
                print('line',lineOfBrack,':',lines[lineOfBrack])
                exit()
        else:
            print('Expected open bracket "[" at line',lineNum)
            print('line',lineNum,':',lines[lineNum])
            exit()
    elif(token == 'opensquarebrackettk'):
        lineOfBrack = lineNum
        lex()
        qTrue,qFalse = condition()
        if(token == 'closesquarebrackettk'):
            lex()
            return (qTrue,qFalse)
        else:
            print('Found open bracket "[" at line',lineOfBrack,'but close bracket "]" not found')
            print('line',lineOfBrack,':',lines[lineOfBrack])
            exit()
    elif(token == 'truetk'):
        qTrue = makeList(nextQuad())
        genQuad('jump','','','')
        qFalse = makeList(nextQuad())
        genQuad('','','','')
        lex()
        return (qTrue,qFalse)
    elif(token == 'falsetk'):
        qTrue = makeList(nextQuad())
        genQuad('','','','')
        qFalse = makeList(nextQuad())
        genQuad('jump','','','')
        lex()
        return (qTrue,qFalse)
    else:
        exp1 = expression()
        relOp = relationalOper()
        exp2 = expression()
        qTrue = makeList(nextQuad())
        genQuad(relOp,exp1,exp2,'')
        qFalse = makeList(nextQuad())
        genQuad('jump','','','')
        return (qTrue,qFalse)


# In[42]:


def expression():
    thisSign = optionalSign()
    t1Place = term()
    if(thisSign == '-'):
        temp = newTemp()
        genQuad('*','-1',t1Place,temp)
        t1Place = temp
    while(token == 'plustk' or token == 'minustk'):
        oper = lexout
        lex()
        t2Place = term()
        w = newTemp()
        genQuad(oper, t1Place, t2Place, w)
        t1Place = w
    ePlace = t1Place
    return ePlace


# In[43]:


def term():
    f1Place = factor()
    while(token == 'multk' or token == 'divtk'):
        oper = lexout
        lex()
        f2Place = factor()
        
        w = newTemp()
        genQuad(oper, f1Place, f2Place, w)
        f1Place = w
    tPlace = f1Place
    return tPlace


# In[44]:


def factor():
    if(token == 'openbrackettk'):
        lineOfBrack = lineNum
        lex()
        output = expression()
        if(token == 'closebrackettk'):
            lex()
            return output
        else:
            print('Found open parenthesis "(" at line',lineOfBrack,'but close parenthesis ")" not found')
            print('line',lineOfBrack,':',lines[lineOfBrack])
            exit()
    elif(token == 'idtk'):
        output = lexout
        lex()
        out = idTail(output)
        if(out is None):
            return output
        else:
            return out
    elif(token == 'consttk'):
        output = lexout
        lex()
        return output
    else:
        print('wrong character',nextChar,'at line:',lineNum)
        print('line',lineNum,':',lines[lineNum])
        exit()


# In[45]:


def idTail(inId):
    out = []
    out = actualPars()
    outVar = None
    if out is not None:
        outVar = newTemp()
        for i in range(len(out)):
            genQuad('par',out[i][0],out[i][1],'')
        genQuad('par',outVar,'ret','')
        genQuad('call',inId,'','')
    return outVar


# In[46]:



def relationalOper():
    if(token == 'equaltk' or token == 'notequaltk' or 
       token == 'lessequaltk' or token == 'greaterequaltk' or
       token == 'greatertk' or token == 'lesstk'):
        output = lexout
        lex()
        return output
    else:
        print('Expected relational operator in condition at line',lineNum)
        print('line',lineNum,':',lines[lineNum])
        exit()


# In[47]:


def optionalSign():
    if(token == 'plustk' or token == 'minustk'):
        sign = token
        lex()
        if(sign == 'minustk'):
            return '-'


# In[48]:


def printStat():
    if(token ==  'printtk'):
        lex()
        ePlace = expression()
        genQuad('print',ePlace,'','')


# In[49]:


def inputStat():
    if(token == 'inputtk'):
        lex()
        if(token == 'idtk'):
            genQuad('input','','',lexout)
            lex()
        else:
            print('Expexted variable after input statement at line',lineNum)
            print('line',lineNum,':',lines[lineNum])
            exit()


# In[50]:


def genQuad(op, x, y, z):
    quads.append([op, x, y, z])


# In[51]:


def nextQuad():
    return(len(quads)) #will return the next quad label (len(quads) = next quad label)


# In[52]:


def newTemp():
    global cnt
    global offsetVal
    temp = 'T_' + str(cnt)
    cnt += 1
    scopes[nestingLevel].append([temp,offsetVal])
    offsetVal += 4
    return(temp)



# In[53]:


def emptyList():
    quadList = []
    return quadList


# In[54]:


def makeList(x):
    outList = emptyList()
    outList.append(x)
    return outList



# In[55]:


def merge(list1,list2):
    list3 = []
    if(list1 is not None):
        for i in list1:
            list3.append(i)
    if(list2 is not None):
        for j in list2:
            list3.append(j)
    return list3




# In[56]:


def backpatch(listIn,z):
    for i in listIn:
        if(quads[i][3] == ''):
            quads[i][3] = str(z)


# In[57]:


def toC(thisFile):
    variables = []
    varStr = ''
    variables = findVars()
    thisFile = thisFile[:-3] + 'c'
    file = open(thisFile,'w')
    file.write('#include <stdio.h>\n#include <stdlib.h>\nint main(){\n')
    for i in variables:
        varStr += i + ','
    varStr = varStr[:-1]    
    file.write('\tint ' + varStr + ';\n')
    for i in range(len(quads)):
        file.write('\tL_' + str(i) + ': ')
        if(quads[i][0] == ':='):
            
            file.write(quads[i][3] + ' = ' + quads[i][1] + ';\n')
        
        elif(quads[i][0] == '*' or quads[i][0] == '/' or
            quads[i][0] == '-' or quads[i][0] == '+'):
            
            file.write(quads[i][3] + ' =(int)(' + quads[i][1] + quads[i][0] + quads[i][2] + ');\n')
        
        elif(quads[i][0] == '<' or quads[i][0] == '<=' or
            quads[i][0] == '>' or quads[i][0] == '>='):
            file.write('if(' + quads[i][1] + ' ' + quads[i][0] + ' ' + quads[i][2] + ') goto L_' + str(quads[i][3]) + ';\n')
        elif(quads[i][0] == 'jump'):
            file.write('goto L_' + str(quads[i][3]) +';\n')
        elif(quads[i][0] == '='):
            file.write('if(' + quads[i][1] + ' ' + '==' + ' ' + quads[i][2] + ') goto L_' + str(quads[i][3]) + ';\n')
        elif(quads[i][0] == '<>'):
            file.write('if(' + quads[i][1] + ' ' + '!=' + ' ' + quads[i][2] + ') goto L_' + str(quads[i][3]) + ';\n')
        elif(quads[i][0] == 'print'):
            file.write('printf("%d\\n",' + quads[i][1] +');\n')
        elif(quads[i][0] == 'input'):
            file.write('scanf(" %d",&' + quads[i][3] +');\n')
        else:
            file.write('\n')
    file.write('\treturn 0;\n}') 
    file.close


# In[58]:


def findVars():
    variables = []
    for i in range(len(quads)):
        if(quads[i][0] == '*' or quads[i][0] == '/' or
           quads[i][0] == ':=' or quads[i][0] == '-' or
           quads[i][0] == '+' or quads[i][0] == 'input' ):
            if(quads[i][3] not in variables):
                variables.append(quads[i][3])
    return variables


# In[59]:


def toInt(thisFile):
    thisFile = thisFile[:-3] + 'int'
    file = open(thisFile,'w')
    for i in range(len(quads)):
        file.write('[' + str(i) + '] ' +str(quads[i][0]) + ' ' + str(quads[i][1]) + ' ' +
                   str(quads[i][2]) + ' ' + str(quads[i][3]) + '\n')
    file.close





filePath = sys.argv[1]
#filePath = 'ex10.eel'
asmFile = open(filePath[:-3]+'asm','w')
asmFile.write('j Lmain\n')
with open(filePath) as f:
    line = f.readline()
    while(line != ''):
        lines[count] = line.strip()
        count += 1
        line = f.readline()
file = open(filePath,"r")
main()
asmFile.close()
print('--->  Program '+ filePath[:-4] +' extract in .int')
print('--->  Program '+ filePath[:-4] +' extract in .asm')
toInt(filePath)
if(notSubProg):
    print('--->  Program '+ filePath[:-4] +' extract in .c')
    toC(filePath)
else:
    print('--->  Program '+ filePath[:-4] +' can not extract in .c')
    print('This .eel program has procedures or functions')
#print(scopes)

