from sly import Lexer, Parser

class ProgramLexer(Lexer):
    tokens = {NEWLINE, NAME, NUMBER, STRING, PRINT,
              IF, ELIF, ELSE, AND, OR, NOT, IS_EQUAL, GREATER_EQUAL, LESS_EQUAL, NOT_EQUAL}

    ignore = '\t '
    literals = {'=', '+', '-', '/', '*', '(', ')',
                '{', '}', ',', ';', ':', '>', '<', '='}

    # Define tokens as regular expressions
    # (stored as raw strings)

    IS_EQUAL = r'=='
    GREATER_EQUAL = r'>='
    LESS_EQUAL = r'<='
    NOT_EQUAL = r'!='

    PRINT = r'print'
    IF = r'if'
    ELIF = r'elif'
    ELSE = r'else'
    AND = r'and'
    OR = r'or'
    NOT = r'not'

    NAME = r'[a-zA-Z_][a-zAZ0-9_]*'
    STRING = r'\".*?\"'

    # Number token
    @_(r'\d+(\.\d+)?')
    def NUMBER(self, t):
        if '.' in t.value:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t

    # Comment token
    @_(r'//.*')
    def COMMENT(self, t):
        pass

    # Newline token(used only for showing
    # errors in new line)
    @_(r'\n+')
    def NEWLINE(self, t):
        self.lineno += t.value.count('\n')
        return t

    @_(r'print')
    def PRINT(self, t):
        return t

class ProgramParser(Parser):
    #tokens are passed from lexer to parser
    tokens = ProgramLexer.tokens

    precedence = (
        ('left', AND, OR),
        ('left', '>', '<', '=', NOT_EQUAL, GREATER_EQUAL, LESS_EQUAL, IS_EQUAL),
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS', NOT),
    )

    def __init__(self):
        self.env = {}

    @_('')  # Empty statement
    def statement(self, p):
        pass

    @_('statement NEWLINE statements')
    def statements(self, p):
        return [p.statement] + p.statements

    @_('statement')
    def statements(self, p):
        return [p.statement]  # Allows single statements

    @_('var_assign')
    def statement(self, p):
        return p.var_assign

    @_('NAME "=" expr')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.expr)

    @_('NAME "=" STRING')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.STRING)

    @_('expr')
    def statement(self, p):
        return p.expr

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('expr "+" expr')
    def expr(self, p):
        return ('add', p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return ('sub', p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return ('mul', p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        return ('div', p.expr0, p.expr1)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return ('neg', p.expr)

    @_('expr ">" expr')
    def expr(self, p):
        return ('greater', p.expr0, p.expr1)

    @_('expr "<" expr')
    def expr(self, p):
        return ('less', p.expr0, p.expr1)

    @_('expr IS_EQUAL expr')
    def expr(self, p):
        return ('is_equal', p.expr0, p.expr1)

    @_('expr NOT_EQUAL expr')
    def expr(self, p):
        return ('not_equal', p.expr0, p.expr1)

    @_('expr GREATER_EQUAL expr')
    def expr(self, p):
        return ('greater_equal', p.expr0, p.expr1)

    @_('expr LESS_EQUAL expr')
    def expr(self, p):
        return ('less_equal', p.expr0, p.expr1)

    @_('expr AND expr')
    def expr(self, p):
        return ('and', p.expr0, p.expr1)

    @_('expr OR expr')
    def expr(self, p):
        return ('or', p.expr0, p.expr1)

    @_('NOT expr')
    def expr(self, p):
        return ('not', p.expr)

    @_('NAME')
    def expr(self, p):
        return ('var', p.NAME)

    @_('NUMBER')
    def expr(self, p):
        return ('num', p.NUMBER)

    @_('PRINT "(" expr ")"')
    def statement(self, p):
        return ('print', p.expr)  # p[1] corresponds to either expr or STRING

    @_('PRINT "(" STRING ")"')
    def statement(self, p):
        return ('print', p.STRING)  # p[1] corresponds to either expr or STRING

    @_('IF "(" expr ")" "{" statements "}"')
    def statement(self, p):
        return ('if_stmt', p.expr, p.statements)

    @_('IF "(" expr ")" "{" statements "}" ELSE "{" statements "}"')
    def statement(self, p):
        return ('if_stmt_else', p.expr, p.statements0, p.statements1)

    @_('IF "(" expr ")" "{" statements "}" elif_blocks ELSE "{" statements "}"')
    def statement(self, p):
        return ('if_stmt_full', p.expr, p.statements0, p.elif_blocks, p.statements1)

    @_('ELIF "(" expr ")" "{" statements "}" elif_blocks')
    def elif_blocks(self, p):
        return [('elif_stmt', p.expr, p.statements)] + p.elif_blocks

    @_('ELSE "{" statements "}"')
    def statement(self, p):
        return ('else_stmt', p.statements)

    @_('')  # Empty elif block case
    def elif_blocks(self, p):
        return []

class ExecuteProgram:
    def __init__(self, tree, env):
        self.env = env
        result = self.walkTree(tree)
        if isinstance(result, (int, float)):  # Print both int and float results
            print(result)
        elif isinstance(result, str) and result.startswith('"'):
            print(result)

    def walkTree(self, node):
        if isinstance(node, (int, float)):  # Handle both int and float
            return node
        if isinstance(node, str):
            return node

        if node is None:
            return None

        if node[0] == 'num':
            return node[1]

        if node[0] == 'neg':
            return -self.walkTree(node[1])

        if node[0] == 'add':
            left = self.walkTree(node[1])
            right = self.walkTree(node[2])
            # If both are strings, concatenate properly (strip quotes before adding)
            if isinstance(left, str) and isinstance(right, str):
                return left.rstrip('"') + right.lstrip('"')  # Concatenate strings without quotes

            # If one is a string, convert the other to string before adding
            if isinstance(left, str) or isinstance(right, str):
                return str(left).strip("\"") + str(right).strip("\"")

            return left + right

        elif node[0] == 'sub':
            return self.walkTree(node[1]) - self.walkTree(node[2])

        elif node[0] == 'mul':
            return self.walkTree(node[1]) * self.walkTree(node[2])

        elif node[0] == 'div':
            denominator = self.walkTree(node[2])
            if denominator == 0:
                print("Error: Division by zero")
                return None
            return self.walkTree(node[1]) / denominator  # Always return float

        if node[0] == 'var_assign':
            self.env[node[1]] = self.walkTree(node[2])
            return node[1]

        if node[0] == 'greater':
            return self.walkTree(node[1]) > self.walkTree(node[2])

        elif node[0] == 'less':
            return self.walkTree(node[1]) < self.walkTree(node[2])

        elif node[0] == 'is_equal':
            return self.walkTree(node[1]) == self.walkTree(node[2])

        elif node[0] == 'not_equal':
            return self.walkTree(node[1]) != self.walkTree(node[2])

        elif node[0] == 'greater_equal':
            return self.walkTree(node[1]) >= self.walkTree(node[2])

        elif node[0] == 'less_equal':
            return self.walkTree(node[1]) <= self.walkTree(node[2])

        if node[0] == 'and':
            return self.walkTree(node[1]) and self.walkTree(node[2])

        elif node[0] == 'or':
            return self.walkTree(node[1]) or self.walkTree(node[2])

        elif node[0] == 'not':
            return not self.walkTree(node[1])

        if node[0] == 'var':
            try:
                return self.env[node[1]]
            except LookupError:
                print(f"Undefined variable '{node[1]}' found!")
                return None

        if node[0] == 'print':
            result = self.walkTree(node[1])
            print(result)
            return None

        if node[0] == 'if_stmt':
            condition = self.walkTree(node[1])
            #print(f"Debug: IF condition evaluated to {condition}")
            if condition:
                for stmt in node[2]:  # Iterate through statements inside `{}`
                    self.walkTree(stmt)  # Execute each statement
                return  # Prevent unnecessary return values

        # Apply similar logic to elif and else blocks
        if node[0] == 'elif_stmt':
            condition = self.walkTree(node[1])
            if condition:
                for stmt in node[2]:
                    self.walkTree(stmt)
                return

        if node[0] == 'else_stmt':
            for stmt in node[1]:  # Ensure the else block executes statements
                self.walkTree(stmt)
            return

        if node[0] == 'if_stmt_else':
            condition = self.walkTree(node[1])
            #print(f"Debug: Evaluating IF condition -> {condition}")  # Debug

            if condition:
                for stmt in node[2]:  # Execute the `if` block
                    self.walkTree(stmt)
            else:
                #print("Debug: Executing ELSE block")  # Debug
                for stmt in node[3]:  # Execute the `else` block
                    self.walkTree(stmt)
            return

        if node[0] == 'if_stmt_full':
            condition = self.walkTree(node[1])
            if condition:
                for stmt in node[2]:
                    self.walkTree(stmt)
                return

            for elif_stmt in node[3]:
                elif_condition = self.walkTree(elif_stmt[1])
                if elif_condition:
                    for stmt in elif_stmt[2]:
                        self.walkTree(stmt)
                    return

            for stmt in node[4]:  # Execute `else` block if no condition matched
                self.walkTree(stmt)
            return

if __name__ == '__main__':
    lexer = ProgramLexer()
    parser = ProgramParser()
    env = {}
    buffer = []  # Store multiple lines

    while True:
        try:
            line = input('SK.bd> ')

            if line.strip().lower() == 'run':  # If user types "run", execute
                if buffer:
                    code = "\n".join(buffer)  # Combine all lines
                    tree = parser.parse(lexer.tokenize(code))
                    ExecuteProgram(tree, env)
                    buffer = []  # Clear buffer after execution
                continue  # Skip processing "run" itself

            if line.strip():  # Ignore empty lines
                buffer.append(line)  # Add to buffer

        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nExiting SK.bd...")
            break  # Exit safely

