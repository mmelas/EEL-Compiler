import sys
global lexout
global lines
lines = {}
count = 1
lineNum = 1
en = 0


# In[47]:

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
  


# In[121]:


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


# In[49]:


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
    
    token = 'idtk'
    if(strToken in tks):
        token = strToken+'tk'
    lexout = strToken
    return(nextChar)


# In[50]:


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
    return(nextChar)


# In[51]:


def main():
    global token
    lex()
    program()


# In[52]:


def program():
    global token
    if token == 'programtk':
        lex()
        if token == 'idtk':
            lineOfProgram = lineNum
            lex()
            block()
            if token == 'endprogramtk':
                lineOfEnd = lineNum
                lex()
                if token != '':
                    print('End of program found at line'
                        ,lineOfEnd,'but there is code below it')
                    print('line',lineOfEnd,':',lines[lineOfEnd])

            else:
               print('Found program at line',lineOfProgram,'but endprogram not found')
               print('line',lineOfProgram,':',lines[lineOfProgram])

        else:
            print('Expected Id for program at line:', lineNum)
            print('line',lineNum,':',lines[lineNum])

    else:
        print('Start of program not found')
        print('line',lineNum,':',lines[lineNum])



# In[53]:


def block():
    declarations()
    subprograms()
    statements()


# In[54]:


def declarations():
    global token
    if token == 'declaretk':
        lineOfDec = lineNum
        lex()
        varlist()
        if token == 'enddeclaretk':
            lex()
        else:
            print('Started declare at line',lineOfDec,'but enddeclare not found')
            print('line',lineOfDec,':',lines[lineOfDec])



# In[55]:


def varlist():
    if token == 'idtk':
        lex()
        while token == 'commatk':
            lex()
            if(token == 'idtk'):
                lex()
                if(token != 'enddeclaretk' and token != 'commatk'):
                    print('Expected comma "," after variable at line',lineNum)
                    print('line',lineNum,':',lines[lineNum])
            else:
                print('variable not found after comma (",") in declarations at line :',lineNum)
                print('line',lineNum,':',lines[lineNum])



# In[56]:


def subprograms():
    while(token == 'proceduretk' or token == 'functiontk'):
        procorfunc()


# In[57]:


def procorfunc():
    if(token == 'proceduretk'):
        lineOfProc = lineNum
        lex()
        if(token == 'idtk'):
            lex()
            procorfuncbody()
            if(token == 'endproceduretk'):
                lex()
            else:
                print('Started procedure at line',lineOfProc,'but endprocedure not found')
                print('line',lineOfProc,':',lines[lineOfProc])
        else:
            print('id not found after procedure declaration at line',lineOfProc)
            print('line',lineOfProc,':',lines[lineOfProc])

    elif(token == 'functiontk'):
        lineOfFunc = lineNum
        lex()
        if(token == 'idtk'):
            lex()
            procorfuncbody()
            if(token == 'endfunctiontk'):
                lex()
            else:
                print('Started procedure at line',lineOfFunc,'but endprocedure not found')
                print('line',lineOfFunc,':',lines[lineOfFunc])
        else:
            print('variable not found after function declaration at line',lineOfFunc)
            print('line',lineOfFunc,':',lines[lineOfFunc])



# In[58]:


def procorfuncbody():
    formalpars()
    block()


# In[59]:


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
    else:
        print('Expected open parenthesis "(" at line',lineNum)
        print('line',lineNum,':',lines[lineNum])


# In[60]:


def formalparlist():
    formalparitem()
    while token == 'commatk':
        lineOfComma = lineNum
        lex()
        if(token == 'intk' or token == 'inouttk'):
            formalparitem()
        else:
            print('Expected in/inout after "," at line',lineOfComma)
            print('line',lineOfComma,':',lines[lineOfComma])


# In[61]:


def formalparitem():
    if token == 'intk' or token == 'inouttk':
        lex()
        if token == 'idtk':
            lex()
        else:
            print('Expected variable after in/inout at line',lineNum)
            print('line',lineNum,':',lines[lineNum])


# In[62]:


def statements():
    statement()
    while token == 'qmarktk':
        lex()
        if (token == 'idtk' or token == 'iftk'
         or token == 'whiletk' or token == 'exittk'
         or token == 'switchtk' or token == 'failuretk' 
         or token == 'calltk' or token == 'returntk'
         or token == 'printtk' or token == 'inputtk' or token == 'repeattk'):
            statement()
    if (token == 'idtk' or token == 'iftk'
         or token == 'whiletk' or token == 'exittk'
         or token == 'switchtk' or token == 'failuretk'
         or token == 'calltk' or token == 'returntk'
         or token == 'printtk' or token == 'inputtk' or token == 'repeattk'):
        print('expected ";" between statements at line',lineNum)
        print('line',lineNum,':',lines[lineNum])


# In[63]:


def statement():
    
    if(token == 'idtk'):
        assignmentStat()
    elif(token == 'iftk'):
        ifStat()
    elif(token == 'whiletk'):
        whileStat()
    elif(token == 'exittk'):
        exitStat()
    elif(token == 'switchtk'):
        switchStat()
    #failureStat()
    elif(token == 'calltk'):
        callStat()
    elif(token == 'forcasetk'):
        forCaseStat()
    elif(token == 'returntk'):
        returnStat()
    elif(token == 'repeattk'):
        repeatStat()
    elif(token == 'printtk'):
        printStat()
    elif(token == 'inputtk'):
        inputStat()   


# In[64]:


def assignmentStat():
    if(token == 'idtk'):
        lex()
        if(token == 'assignmenttk'):
            lex()
            expression()
        else:
            print('expression expected after ":=" at line',lineNum)
            print('line',lineNum,':',lines[lineNum])
        


# In[65]:


def ifStat():
    if(token == 'iftk'):
        lineOfIf = lineNum
        lex()
        condition()
        if(token == 'thentk'):
            lex()
            statements()
            elsePart()
            if(token == 'endiftk'):
                lex()
            else:
                print('Found if statement at line',lineOfIf,'but endif not found')
                print('line',lineOfIf,':',lines[lineOfIf])
        else:
            print('Expected "then" after if statement at line',lineOfIf)
            print('line',lineOfIf,':',lines[lineOfIf])


# In[66]:


def elsePart():
    if(token == 'elsetk'):
        lex()
        statements()


# In[67]:


def repeatStat():
    if(token == 'repeattk'):
        lineOfRep = lineNum
        lex()
        statements()
        if(token == 'endrepeattk'):
            lex()
        else:
            print('Found repeat statement at line',lineOfRep,'but endrepeat not found',)
            print('line',lineOfRep,':',lines[lineOfRep])


# In[68]:


def exitStat():
    if(token == 'exittk'):
        lex()
    


# In[69]:


def whileStat():
    if(token == 'whiletk'):
        lineOfWhile = lineNum
        lex()
        condition()
        statements()
        if(token == 'endwhiletk'):
            lex()
        else:
            print('Found while statement at line',lineOfWhile,'but endwhile not found',)
            print('line',lineOfWhile,':',lines[lineOfWhile])

# In[70]:


def switchStat():
    if(token == 'switchtk'):
        lineOfSwitch = lineNum
        lex()
        expression()
        if(token == 'casetk'):
            lineOfCase = lineNum
            lex()
            expression()
            if(token == 'colontk'):
                lex()
                statements()
            else:
                print('Expected ":" after expression in case at line',lineOfCase)
                print('line',lineOfCase,':',lines[lineOfCase])
        else:
            print('At least one case needed for switch at line',lineOfSwitch)
            print('line',lineOfSwitch,':',lines[lineOfSwitch])
        while(token == 'casetk'):
            lineOfCase = lineNum
            lex()
            expression()
            if(token == 'colontk'):
                lex()
                statements()
            else: 
                print('Expected ":" after expression in case at line',lineOfCase)
                print('line',lineOfCase,':',lines[lineOfCase])
        if(token == 'endswitchtk'):
            lex()
        else:
            print('Found switch statement at line',lineOfSwitch,'but endswitch not found')
            print('line',lineOfSwitch,':',lines[lineOfSwitch])


# In[71]:


def forCaseStat():
    if(token == 'forcasetk'):
        lineOfFor = lineNum
        lex()
        if(token == 'whentk'):
            lineOfWhen = lineNum
            lex()
            condition()
            if(token == 'colontk'):
                lex()
                statements()
            else:
                print('Expected ":" after condition in for statement at line',lineNum)
                print('line',lineOfWhen,':',lines[lineOfWhen])
        else:
            print('At least one when needed for forcase at line',lineOfFor)
            print('line',lineOfFor,':',lines[lineOfFor])
        while(token == 'whentk'):
            lineOfWhen = lineNum
            lex()
            condition()
            if(token == 'colontk'):
                lex()
                statements()
            else:
                print('Expected ":" after condition in for statement at line',lineNum)
                print('line',lineOfWhen,':',lines[lineOfWhen])
        if(token == 'endforcasetk'): 
            lex()
        else:
            print('Found forcase statement at line',lineOfFor,'but endforcase not found')
            print('line',lineOfFor,':',lines[lineOfFor])


# In[72]:


def callStat():
    if(token == 'calltk'):
        lex()
        if(token == 'idtk'):
            lex()
            actualPars()
        else:
            print('Expected function after call statement at line', lineNum)
            print('line',lineNum,':',lines[lineNum])


# In[73]:


def actualPars():
    if(token == 'openbrackettk'):
        lineOfBrack = lineNum
        lex()
        actualParList()
        if(token == 'closebrackettk'):
            lex()
        else:
            print('Found open parenthesis "(" at line',lineOfBrack,'but close parenthesis ")" not found')
            print('line',lineOfBrack,':',lines[lineOfBrack])


# In[74]:


def actualParList():
    if(token != 'closebrackettk'):
        actualParItem()
        while(token == 'commatk'):
            lex()
            actualParItem()
            


# In[75]:


def actualParItem():
    if(token == 'intk'):
        lex()
        expression()
    elif(token == 'inouttk'):
        lex()
        if(token == 'idtk'):
            lex()
        else:
            print('Expected variable after "inout" at line',lineNum)
            print('line',lineNum,':',lines[lineNum])
    else:
        print('Expected in/inout expression after "," at line',lineNum)
        print('line',lineNum,':',lines[lineNum])



# In[76]:


def returnStat():
    if(token == 'returntk'):
        lex()
        expression()


# In[77]:


def condition():
    boolterm()
    while(token == 'ortk'):
        lex()
        boolterm()


# In[78]:


def boolterm():
    boolfactor()
    while(token == 'andtk'):
        lex()
        boolfactor()


# In[79]:


def boolfactor():
    if(token == 'nottk'):
        lex()
        if(token == 'opensquarebrackettk'):
            lineOfBrack = lineNum
            lex()
            condition()
            if(token == 'closesquarebrackettk'):
                lex()
            else:
                print('Found open bracket "[" at line',lineOfBrack,'but close bracket "]" not found')
                print('line',lineOfBrack,':',lines[lineOfBrack])
        else:
            print('Expected open bracket "[" at line',lineNum)
            print('line',lineNum,':',lines[lineNum])
    elif(token == 'opensquarebrackettk'):
        lineOfBrack = lineNum
        lex()
        condition()
        if(token == 'closesquarebrackettk'):
                lex()
        else:
            print('Found open bracket "[" at line',lineOfBrack,'but close bracket "]" not found')
            print('line',lineOfBrack,':',lines[lineOfBrack])
    elif(token == 'truetk'):
        lex()
    elif(token == 'falsetk'):
        lex()
    else:
        expression()
        relationalOper()
        expression()


# In[80]:


def expression():
    optionalSign()
    term()
    while(token == 'plustk' or token == 'minustk'):
        lex()
        term()


# In[81]:


def term():
    factor()
    while(token == 'multk' or token == 'divtk'):
        lex()
        factor()


# In[82]:


def factor():
    if(token == 'openbrackettk'):
        lineOfBrack = lineNum
        lex()
        expression()
        if(token == 'closebrackettk'):
            lex()
        else:
            print('Found open parenthesis "(" at line',lineOfBrack,'but close parenthesis ")" not found')
            print('line',lineOfBrack,':',lines[lineOfBrack])
    elif(token == 'idtk'):
        lex()
        idTail()
    elif(token == 'consttk'):
        lex()
    else:
        print('wrong character',nextChar,'at line:',lineNum)
        print('line',lineNum,':',lines[lineNum])

# In[83]:


def idTail():
    actualPars()


# In[84]:


def relationalOper():
    if(token == 'equaltk' or token == 'notequaltk' or 
       token == 'lessequaltk' or token == 'greaterequaltk' or
       token == 'greatertk' or token == 'lesstk'):
        lex()
    else:
        print('Expected relational operator in condition at line',lineNum)
        print('line',lineNum,':',lines[lineNum])


# In[85]:


def optionalSign():
    if(token == 'plustk' or token == 'minustk'):
        lex()


# In[86]:


def printStat():
    if(token ==  'printtk'):
        lex()
        expression()
    


# In[87]:


def inputStat():
    if(token == 'inputtk'):
        lex()
        if(token == 'idtk'):
            lex()
        else:
            print('Expexted variable after input statement at line',lineNum)
            print('line',lineNum,':',lines[lineNum])

filePath = sys.argv[1]

with open(filePath) as f:
    line = f.readline()
    while(line != ''):
        lines[count] = line.strip()
        count += 1
        line = f.readline()
file = open(filePath,"r")
main()


