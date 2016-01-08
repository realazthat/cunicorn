


import sys



class AstLine:
    def __init__(self, parent, name, identifer, line_data, children=[]):
        self.parent = parent
        self.name = name
        self.identifer = identifer
        self.line_data = line_data
        self.children = list(children)

class FunctionDeclLine(AstLine):
    def __init__(self, parent, identifer, line_data, children=[]):
        AstLine.__init__(self, parent, 'FunctionDecl', line_data)

def parse_ast_line(parent, name, identifer, line_data):
    if name == 'FunctionDecl':
        return FunctionDeclLine(parent, name, identifer, line_data)

    return AstLine(parent, name, identifer, line_data)

class Ast:
    
    def __init__(self, parent, identifier, astline):
        self.parent = parent
        self.identifier = identifier
        self.astline = astline
        
class FunctionAst(Ast):
    def __init__(self, parent, astline, funcname, arguments, body):
        Ast.__init__(self,parent,astline.identifier,astline)
        self.funcname = funcname
        self.arguments = list(arguments)
        self.body = body
class ParmVarDeclAst(Ast):
    def __init__(self, parent, astline, varname, typename):
        Ast.__init__(self,parent,astline.identifier,astline)
        self.varname = varname
        self.typename = typename
        
def to_ast(astline):
    
    if astline.name == 'FunctionDecl':
        func = FunctionAst(None, astline, astline.identifier, funcname, arguments=[], body=[])
        for childastline in astline.children:
            if childastline.name == 'ParmVarDecl':
                childast = to_ast(childastline)
                childast.parent = func
                func.arguments += [childast]
            elif childastline.name == 'CompoundStmt':
                body = to_ast(childastline)
                body.parent = func
                func.body = body
            else:
                assert False, childastline.name
                
        return func
    elif astline.name == 'ParmVarDecl':
        name,_,line_data_after_name = line_data.partition(' ')
        identifer,_,line_data_after_id = line_data_after_name.partition(' ')
        _,_,line_data_after_span = line_data_after_id.partition('> ')
        _,_,line_data_col = line_data_after_span.partition(' ')
        used,_,line_data_after_used = line_data_col.partition(' ')
        varname,_,line_data_after_varname = line_data_after_used.partition(' ')

        #todo: fix this
        typename = ''
        return ParmVarDeclAst(None, astline, varname, typename)
    else:
        assert False, astline.name

def main():
    linelist = []
    root = None
    current_parent = None
    current_indent = 0
    for line0 in sys.stdin:
        line_data = line0;
        indentation = ''
        if root is not None:
            
            indentation, _, line_data = line_data.partition('-')
            
        if len(indentation) < current_indent:
            assert current_parent is not None
            current_parent = current_parent.parent
            current_indent -= 2
        if current_indent == 0:
            assert current_parent is None
        else:
            assert current_parent is not None
    
        name,_,line_data_after_name = line_data.partition(' ')
        identifer,_,line_data_after_id = line_data_after_name.partition(' ')
        astline = parse_ast_line(current_parent,name,identifer,line_data)
        
        current = astline
        linelist += [astline]
        
        if root is None:
            root = astline
        if current_parent is not None:
            current_parent.children += [astline]



if __name__ == '__main__':
    main()
