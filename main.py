




import sys
from clang34.cindex import Index, CursorKind, Config
#from clang37.cindex import Index, CursorKind, Config
from optparse import OptionParser, OptionGroup
#import yaml


class FunctionMetaData:
    def __init__(self, symbol_name, cursor):
        self.symbol_name = symbol_name
        self.cursor = cursor

# {symbol_name => FunctionMetaData}
functions = {}


def walk_preorder(cursor, depth=0):
    """Depth-first preorder walk over the cursor and its descendants.
    Yields cursors.
    """
    yield (cursor,depth)
    
    for child in cursor.get_children():
        for (descendant,ddepth) in walk_preorder(child,depth+1):
            yield (descendant,ddepth)

def get_info(node, depth=0):

    children = [get_info(c, depth+1)
                for c in node.get_children()]
    return { #'id' : get_cursor_id(node),
             'kind' : node.kind,
             'usr' : node.get_usr(),
             'spelling' : node.spelling,
             'location' : node.location,
             'extent.start' : node.extent.start,
             'extent.end' : node.extent.end,
             'is_definition' : node.is_definition(),
             #'definition id' : get_cursor_id(node.get_definition()),
             'children' : children }

def dump_cursor(cursor,indent_depth=0, indentation='  ', name='cursor'):
    
    #print (get_info(cursor))
    #return
    
    for cursor1,depth in walk_preorder(cursor):
        indent = (indentation*(indent_depth+depth))
        indent2 = (indentation*(indent_depth+depth+2))
        msg = '{indent}{name}.kind: {kind}, {name}.displayname: {displayname}, len({name}.get_children()): {numchildren}'
        msg = msg.format( indent=indent
                        , name=name
                        , kind=repr(cursor1.kind)
                        , displayname=repr(cursor1.displayname)
                        , numchildren=len(list(cursor1.get_children())))
        print (msg)
        msg = '{indent2}- len({name}.get_arguments()): {numargs}, {name}.spelling: {spelling}, {name}.result_type: {result_type}'
        msg = msg.format( indent2=indent2
                        , name=name
                        , numargs=len(list(cursor1.get_arguments()))
                        , spelling=repr(cursor1.spelling)
                        , result_type=cursor1.get_usr() #'<not implemented>' #list(cursor1.get_tokens())
                        )
        print (msg)
    
def find_all_dependent_symbols(predicate):
    symbols = set()
    if predicate.kind == CursorKind.CALL_EXPR:
        for arg_cursor in predicate.get_arguments():
            symbols |= find_all_dependent_symbols(arg_cursor)
        
    elif predicate.kind == CursorKind.DECL_REF_EXPR:
        symbols.add(predicate.displayname)
    elif predicate.kind == CursorKind.BINARY_OPERATOR:
        for child_cursor in predicate.get_children():
            symbols |= find_all_dependent_symbols(child_cursor)
    elif predicate.kind == CursorKind.UNEXPOSED_EXPR and len(list(predicate.get_children())) == 1:
        child, = predicate.get_children()
        symbols |= find_all_dependent_symbols(child)
    else:
        dump_cursor(predicate)
        assert False, predicate.kind
    return symbols


class Predicate:
    def compute_variables(self):
        raise NotImplementedError();
    def evaluate(self, variable_values={}):
        raise NotImplementedError();

class Not(Predicate):
    def __init__(self, operand):
        Predicate.__init__(self)
        self.operand = operand
    

class And(Predicate):
    def __init__(self, operands):
        Predicate.__init__(self)
        self.operands = operands

class Or(Predicate):
    def __init__(self, operands):
        Predicate.__init__(self)
        self.operands = operands

class Expression:
    def __init__(self):
        self.result_type = None

class Comparison(Predicate):
    def __init__(self, left, right):
        Predicate.__init__(self)
        assert isinstance(left, Expression)
        assert isinstance(right, Expression)
        self.left = left
        self.right = right


class Function(Expression):
    def __init__(self, name, operands, result_type):
        Expression.__init__(self)
        for operand in operands:
            assert isinstance(left, Expression)
        self.name = name
        self.operands = operands
        self.result_type = return_type


class BoolFunction(Function):
    def __init__(self, name, operands):
        Function.__init__(self)
        for operand in operands:
            assert isinstance(left, Expression)
        self.name = name
        self.operands = operands
        self.result_type = 'bool'

class VariableExpression(Expression):
    def __init__(self, name, result_type):
        Expression.__init__(self)
        self.result_type = result_type

def extract_logical_predicate(pcursor):
    
    if pcursor.kind == CursorKind.CALL_EXPR:
        if pcursor.displayname == 'valid_memory':
            operands = []
            for acursor in pcursor.get_arguments():
                operands += extract_logical_predicate(acursor)
            
            return Function(name='valid_memory', operands=operands, result_type='bool')
        dump_cursor(pcursor)
        assert False, pcursor.kind
    elif pcursor.kind == CursorKind.DECL_REF_EXPR:
        symbols.add(pcursor.displayname)
    elif pcursor.kind == CursorKind.BINARY_OPERATOR:
        assert len(list(pcursor.get_children())) == 2
        left, right = pcursor.get_children()
        
        dump_cursor(pcursor)
        assert False, pcursor.kind
        
    elif pcursor.kind == CursorKind.UNEXPOSED_EXPR and len(list(pcursor.get_children())) == 1:
        child, = pcursor.get_children()
        return extract_logical_predicate(child)
    else:
        dump_cursor(pcursor)
        assert False, pcursor.kind
        

def add_assumption(fmeta, statement_cursor):
    
    arg_cursors = list(statement_cursor.get_arguments())
    
    predicate_cursor = arg_cursors[0]
    
    named_params = arg_cursors[1:]
    
    #symbols = find_all_dependent_symbols(predicate)
    
    
    dump_cursor(predicate_cursor)
    lpred = extract_logical_predicate(predicate_cursor)
    
    print ('symbols:', symbols)
    
    
def precondition_pass(f):
    global functions
    
    assert f.displayname not in functions
    fmeta = functions[f.displayname] = FunctionMetaData(f.displayname, f)
    
    print ('f.kind:',f.kind, 'f.displayname:',f.displayname)

    for cursor,depth in walk_preorder(f):
        #print ('    cursor.kind:',cursor.kind, 'cursor.displayname:',cursor.displayname)
        
        if cursor.kind == CursorKind.CALL_EXPR and cursor.displayname == 'contract_assume':
            add_assumption(fmeta, cursor)


def main():


    parser = OptionParser("usage: %prog [options] {filename} [clang-args*]")
    parser.disable_interspersed_args()
    (opts, args) = parser.parse_args()
    if len(args) == 0:
        parser.error('invalid number arguments')

    # FIXME: Add an output file option
    out = sys.stdout
    Config.set_library_file('libclang-3.4.so.1')
    Config.set_library_path('/usr/lib/x86_64-linux-gnu/')
    #Config.set_library_file('libclang.dll')
    #Config.set_library_path('~/.local/bin')
    
    index = Index.create()
    tu = index.parse(None, args)
    if not tu:
        parser.error("unable to load input")


    
    cursor0 = tu.cursor
    
    
    for cursor,depth in walk_preorder(cursor0):
        if cursor.kind == CursorKind.FUNCTION_DECL:
            precondition_pass(cursor)
    
    
    

if __name__ == '__main__':
    main()
