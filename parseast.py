


import sys



class AstLine:
    def __init__(self, parent, name, line_data, children=[]):
        self.parent = parent
        self.name = name
        self.line_data = line_data
        self.children = list(children)


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
    
        name,_,line_data = line_data.partition(' ')
        address,_,line_data = line_data.partition(' ')
        astline = AstLine(current_parent, name, line_data)
        
        current = astline
        linelist += [astline]
        
        if root is None:
            root = astline
        if current_parent is not None:
            current_parent.children += [astline]



if __name__ == '__main__':
    main()
