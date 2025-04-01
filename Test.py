from sly import Lexer, Parser

class BrainrotLexer(Lexer):
    tokens = {
        # Core tokens
        HAWK, TUAH, STRING, NUMBER, ID, NEWLINE,
        LPAREN, RPAREN, COLON,
        PLUS, MINUS, MULT, DIV,
        EQ, NE, LT, GT, LTE, GTE, ASSIGN,

        # Implemented brainrot keywords
        GOON, FRFR, YEET, CAP, NOCAP, VIBING, EDGE
    }

    ignore = ' \t'
    ignore_comment = r'\#.*'

    # Literals
    STRING = r'\"([^\\\"]|\\.)*\"'
    NUMBER = r'\d+\.\d*|\d+'
    NEWLINE = r'\n+'

    # Operators
    PLUS = r'\+'
    MINUS = r'-'
    MULT = r'\*'
    DIV = r'/'
    EQ = r'=='
    NE = r'!='
    LT = r'<'
    GT = r'>'
    LTE = r'<='
    GTE = r'>='
    ASSIGN = r'='

    # Symbols
    LPAREN = r'\('
    RPAREN = r'\)'
    COLON = r':'

    # Implemented keywords
    HAWK = r'hawk'
    TUAH = r'tuah'
    GOON = r'goon'
    FRFR = r'frfr'
    YEET = r'yeet'
    CAP = r'cap'
    NOCAP = r'nocap'
    VIBING = r'vibing'
    EDGE = r'edge'

    # Identifier
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'

    def error(self, t):
        print(f"❌ Brainrot error at line {self.lineno}: Illegal char '{t.value[0]}'")
        self.index += 1


class BrainrotParser(Parser):
    tokens = BrainrotLexer.tokens

    precedence = (
        ('left', PLUS, MINUS),
        ('left', MULT, DIV),
        ('nonassoc', LT, GT, LTE, GTE, EQ, NE),
    )

    def __init__(self):
        self.env = {}
        self.result = None

    @_('statements')
    def program(self, p):
        # Filter out None values and flatten any nested lists
        results = []
        for stmt in p.statements:
            if stmt is not None:
                results.append(stmt)
        return results

    @_('statement')
    def statements(self, p):
        return [p.statement]

    @_('statement NEWLINE')
    def statements(self, p):
        return [p.statement]

    @_('statement NEWLINE statements')
    def statements(self, p):
        return [p.statement] + p.statements

    @_('NEWLINE')
    def statements(self, p):
        return []

    @_('NEWLINE statements')
    def statements(self, p):
        return p.statements

    # Statements

    @_('TUAH LPAREN expr RPAREN')
    def statement(self, p):
        value = p.expr
        if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
            # print(value[1:-1])
            return value[1:-1]
        else:
            return value

    @_('HAWK LPAREN RPAREN')
    def statement(self, p):
        user_input = input("BRAINROT>>")
        return f'"{user_input}"'

    """
    @_('TUAH LPAREN STRING RPAREN')
    def statement(self, p):
        # print(p.STRING[1:-1])
        return p.STRING[1:-1]"""

    @_('ID ASSIGN expr')
    def statement(self, p):
        self.env[p.ID] = p.expr
        return None

    @_('ID ASSIGN STRING')
    def statement(self, p):
        self.env[p.ID] = p.STRING  # Store string with quotes
        return None

    # Original if statement without else
    @_('GOON expr COLON NEWLINE statements')
    def statement(self, p):
        if p.expr:
            for stmt in p.statements:
                if stmt is not None:
                    return stmt
        return None

    @_('GOON expr COLON NEWLINE statements EDGE COLON NEWLINE statements')
    def statement(self, p):
        if p.expr:
            for stmt in p.statements0:
                if stmt is not None:
                    return stmt
        else:
            for stmt in p.statements1:
                if stmt is not None:
                    return stmt
        return None

    @_('FRFR ID VIBING expr COLON NEWLINE statements')
    def statement(self, p):
        results = []
        for i in range(p.expr):
            self.env[p.ID] = i
            for stmt in p.statements:
                if stmt is not None:
                    results.append(stmt)
        return results

    @_('YEET expr')
    def statement(self, p):
        return p.expr

    # Expressions
    @_('expr PLUS expr')
    def expr(self, p):
        return p.expr0 + p.expr1

    @_('expr MINUS expr')
    def expr(self, p):
        return p.expr0 - p.expr1

    @_('expr MULT expr')
    def expr(self, p):
        return p.expr0 * p.expr1

    @_('expr DIV expr')
    def expr(self, p):
        return p.expr0 / p.expr1

    @_('expr LT expr')
    def expr(self, p):
        return p.expr0 < p.expr1

    @_('expr GT expr')
    def expr(self, p):
        return p.expr0 > p.expr1

    @_('expr LTE expr')
    def expr(self, p):
        return p.expr0 <= p.expr1

    @_('expr GTE expr')
    def expr(self, p):
        return p.expr0 >= p.expr1

    @_('expr EQ expr')
    def expr(self, p):
        return p.expr0 == p.expr1

    @_('expr NE expr')
    def expr(self, p):
        return p.expr0 != p.expr1

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('NUMBER')
    def expr(self, p):
        if '.' in p.NUMBER:
            return float(p.NUMBER)
        return int(p.NUMBER)

    @_('STRING')
    def expr(self, p):
        return p.STRING

    @_('ID')
    def expr(self, p):
        return self.env.get(p.ID, 0)

    @_('CAP')
    def expr(self, p):
        return "cap"

    @_('NOCAP')
    def expr(self, p):
        return "nocap"

    @_('HAWK LPAREN RPAREN')
    def expr(self, p):
        user_input = input("BRAINROT>>")
        return f'"{user_input}"'

# REPL Interface
lexer = BrainrotLexer()
parser = BrainrotParser()

print("""
🔥 BRAINROT COMPILER v1.0 🔥
Type your code line by line
'SLAYY' to execute | 'GGS' to quit
""")

code_lines = []
while True:
    try:
        line = input("BRAINROT> ").strip()

        if line.lower() == "ggs":
            print("Compilation finished! GG! 🎮")
            break
        elif line.lower() == "slayy":
            if not code_lines:
                print("No code to execute!")
                continue

            full_code = "\n".join(code_lines)
            try:
                result = parser.parse(lexer.tokenize(full_code + "\n"))
                if result:
                    # Changed to print the actual result instead of the list
                    if isinstance(result, str):
                        print(f"➡️ Result: {result}")
                    elif isinstance(result, list) and len(result) > 0:
                        print(f"➡️ Result: {result[0]}")
                    else:
                        print(f"➡️ Result: {result}")
            except Exception as e:
                print(f"💥 Runtime error: {str(e)}")
            code_lines = []
        else:
            if line:
                code_lines.append(line)
    except KeyboardInterrupt:
        print("\nEmergency exit! GG!")
        break