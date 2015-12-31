




import sys
from clang.cindex import Index, CursorKind
from optparse import OptionParser, OptionGroup



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
    
def dump_cursor(cursor,indent_depth=0, indentation='  ', name='cursor'):
    
    
    for cursor1,depth in walk_preorder(cursor):
        indent = (indentation*(indent_depth+depth))
        indent2 = (indentation*(indent_depth+depth+2))
        msg = '{indent}{name}.kind: {kind}, {name}.displayname: {displayname}, len({name}.get_children()): {numchildren}'
        msg = msg.format( indent=indent
                        , name=name
                        , kind=cursor1.kind
                        , displayname=cursor1.displayname
                        , numchildren=len(list(cursor1.get_children())))
        print (msg)
        msg = '{indent2}- len({name}.get_arguments()): {numargs}'
        msg = msg.format( indent2=indent2
                        , name=name
                        , numargs=len(list(cursor1.get_arguments())))
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
        dump_cursor(statement_cursor)
        dump_cursor(predicate)
        assert False, predicate.kind
    return symbols

def add_assumption(fmeta, statement_cursor):
    symbols = set()
    
    arg_cursors = list(statement_cursor.get_arguments())
    
    predicate = arg_cursors[0]
    
    named_params = arg_cursors[1:]
    
    find_all_dependent_symbols(predicate)
    
    print ('symbols:', symbols)
    
def precondition_pass(f):
    global functions
    
    assert f.displayname not in functions
    fmeta = functions[f.displayname] = FunctionMetaData(f.displayname, f)
    
    print ('f.kind:',f.kind, 'f.displayname:',f.displayname)

    for cursor in f.walk_preorder():
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

    index = Index.create()
    tu = index.parse(None, args)
    if not tu:
        parser.error("unable to load input")


    
    cursor0 = tu.cursor
    
    
    for cursor in cursor0.walk_preorder():
        if cursor.kind == CursorKind.FUNCTION_DECL:
            precondition_pass(cursor)
    
    
    

if __name__ == '__main__':
    main()
