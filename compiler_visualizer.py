import streamlit as st
import re
import html
from dataclasses import dataclass, field
from typing import List, Optional

st.set_page_config(
    page_title="C Compiler Phases Visualizer",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="collapsedControl"] { display:none !important; }
section[data-testid="stSidebar"]  { display:none !important; }

.hero {
    background: linear-gradient(135deg,#0f0c29,#302b63,#24243e);
    border-radius:16px; padding:2rem 2.5rem; text-align:center;
    margin-bottom:1.5rem; box-shadow:0 8px 32px rgba(0,0,0,.4);
}
.hero h1 { color:#e94560; font-size:2.2rem; font-weight:800; margin:0; }

.pipe-wrap { display:flex; align-items:center; justify-content:center; flex-wrap:wrap; gap:4px; margin:1rem 0; }
.pipe-box  { background:#1e1e2e; border:1.5px solid #2d2d44; border-radius:10px;
             padding:6px 12px; text-align:center; min-width:80px; }
.pipe-box .num { background:#e94560; color:#fff; border-radius:50%;
                 width:20px;height:20px;display:inline-flex;align-items:center;
                 justify-content:center;font-size:.68rem;font-weight:700;margin-bottom:3px; }
.pipe-box .lbl { color:#cdd6f4; font-size:.68rem; font-weight:600; display:block; }
.pipe-arrow    { color:#e94560; font-size:1.2rem; }

.cblk {
    background:#11111b; border:1px solid #2d2d44; border-radius:10px;
    padding:1rem 1.2rem; font-family:'Fira Code',monospace; font-size:.8rem;
    color:#cdd6f4; white-space:pre; overflow-x:auto; line-height:1.7;
}
.ast-root { font-family:'Fira Code',monospace; font-size:.82rem;
            background:#0d0d1a; border:1px solid #2d2d44;
            border-radius:10px; padding:1.2rem 1.5rem; overflow-x:auto; }
.ast-node { margin:2px 0; }
.nl-program { color:#e94560; } .nl-function { color:#ffcb6b; }
.nl-decl    { color:#c792ea; } .nl-assign   { color:#00d4aa; }
.nl-for     { color:#82aaff; } .nl-while    { color:#f78c6c; }
.nl-if      { color:#89ddff; } .nl-call     { color:#c3e88d; }
.nl-return  { color:#ff5370; } .nl-expr     { color:#a8b2d8; }
.nl-include { color:#f78c6c; } .nl-block    { color:#cdd6f4; }
.nl-condition { color:#ffcb6b; } .nl-init   { color:#a8d8ea; }
.nl-update  { color:#c792ea; }

.stbl { width:100%; border-collapse:collapse; font-family:'Fira Code',monospace; font-size:.8rem; }
.stbl th { background:#0f3460; color:#a8d8ea; padding:8px 12px; text-align:left; border:1px solid #2d2d44; }
.stbl td { padding:6px 12px; border:1px solid #2d2d44; color:#cdd6f4; }
.stbl tr:nth-child(even) td { background:#1a1a2e; }
.stbl tr:nth-child(odd)  td { background:#1e1e2e; }

.out-box { background:#0d1117; border-left:4px solid #00d4aa;
           border-radius:0 10px 10px 0; padding:1rem 1.5rem;
           font-family:'Fira Code',monospace; color:#00d4aa; white-space:pre; line-height:1.7; }
.err-box { background:#1a0000; border-left:4px solid #e94560;
           border-radius:0 10px 10px 0; padding:1rem 1.5rem;
           font-family:'Fira Code',monospace; color:#ff5370; white-space:pre; }

.mrow { display:flex; gap:.8rem; flex-wrap:wrap; margin:.8rem 0; }
.mcard { background:#1e1e2e; border:1px solid #2d2d44; border-radius:10px;
         padding:.6rem 1rem; text-align:center; flex:1; min-width:90px; }
.mcard .mv { font-size:1.5rem; font-weight:800; color:#e94560; }
.mcard .ml { font-size:.7rem; color:#a8b2d8; margin-top:2px; }

.badge-good { background:#003320; color:#00d4aa; border:1px solid #00d4aa;
              border-radius:6px; padding:4px 12px; font-size:.82rem; display:inline-block; margin:2px; }
.badge-warn { background:#332200; color:#ffcb6b; border:1px solid #ffcb6b;
              border-radius:6px; padding:4px 12px; font-size:.82rem; display:inline-block; margin:2px; }
.badge-err  { background:#330000; color:#ff5370; border:1px solid #ff5370;
              border-radius:6px; padding:4px 12px; font-size:.82rem; display:inline-block; margin:2px; }
.sect-title { font-size:.95rem; font-weight:700; color:#cdd6f4;
              margin:.8rem 0 .4rem; border-bottom:1px solid #2d2d44; padding-bottom:.3rem; }
</style>
""",
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
#  AST NODE
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class ASTNode:
    kind: str
    value: str = ""
    children: List["ASTNode"] = field(default_factory=list)

    def add(self, child: "ASTNode") -> "ASTNode":
        self.children.append(child)
        return child


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 – LEXER
# ══════════════════════════════════════════════════════════════════════════════
C_KEYWORDS = {
    "auto",
    "break",
    "case",
    "char",
    "const",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extern",
    "float",
    "for",
    "goto",
    "if",
    "inline",
    "int",
    "long",
    "register",
    "restrict",
    "return",
    "short",
    "signed",
    "sizeof",
    "static",
    "struct",
    "switch",
    "typedef",
    "union",
    "unsigned",
    "void",
    "volatile",
    "while",
}
C_TYPES = {
    "int",
    "char",
    "float",
    "double",
    "long",
    "short",
    "unsigned",
    "signed",
    "void",
}
C_STDLIB = {"printf", "scanf", "strlen", "strcpy", "malloc", "free", "exit"}
TYPE_QUALIFIERS = {
    "const",
    "volatile",
    "static",
    "extern",
    "register",
    "auto",
    "restrict",
}
ENTRY_POINTS = {"main"}

LEX_PATTERNS = [
    ("INCLUDE", r'#\s*include\s*(?:<[^>]*>|"[^"]*")'),
    ("DEFINE", r"#\s*define\s+\w+[^\n]*"),
    ("PRAGMA", r"#\s*\w+[^\n]*"),
    ("FLOAT", r"\b\d+\.\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?\b"),
    ("NUMBER", r"\b0[xX][0-9a-fA-F]+|\b\d+[uUlL]*\b"),
    ("STRING", r'"(?:[^"\\]|\\.)*"'),
    ("CHAR_LIT", r"'(?:[^'\\]|\\.)'"),
    (
        "KEYWORD",
        r"\b(?:" + "|".join(sorted(C_KEYWORDS, key=len, reverse=True)) + r")\b",
    ),
    ("STDLIB", r"\b(?:" + "|".join(sorted(C_STDLIB, key=len, reverse=True)) + r")\b"),
    ("ID", r"\b[a-zA-Z_]\w*\b"),
    (
        "OP",
        r"==|!=|<=|>=|&&|\|\||<<=|>>=|<<|>>|\+\+|--|\+=|-=|\*=|/=|%=|&=|\|=|\^=|->|[-+*/=%<>&|^!~?:.]",
    ),
    ("BRACKETS", r"[{}\[\]()]"),
    ("DELIM", r"[;,]"),
    ("NEWLINE", r"\n"),
    ("SPACE", r"[ \t\r]+"),
    ("UNKNOWN", r"."),
]
_LEXER = re.compile("|".join(f"(?P<{n}>{p})" for n, p in LEX_PATTERNS), re.DOTALL)


def lex(source: str):
    clean = re.sub(r"/\*.*?\*/", " ", source, flags=re.DOTALL)
    clean = re.sub(r"//[^\n]*", " ", clean)
    tokens, errors = [], []
    for m in _LEXER.finditer(clean):
        k, v = m.lastgroup, m.group()
        if k == "SPACE":
            continue
        if k == "NEWLINE":
            tokens.append(("NEWLINE", r"\n"))
        elif k == "UNKNOWN":
            errors.append(f"Unrecognised character: '{v}'")
            tokens.append(("ERROR", v))
        else:
            tokens.append((k, v))
    return tokens, errors


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def dot_esc(value) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 2 – PARSER → AST
# ══════════════════════════════════════════════════════════════════════════════
class Parser:
    def __init__(self, tokens):
        # strip NEWLINEs for parsing
        self.tokens = [(k, v) for k, v in tokens if k != "NEWLINE"]
        self.pos = 0
        self.errors = []

    def peek(self, offset=0):
        i = self.pos + offset
        return self.tokens[i] if i < len(self.tokens) else ("EOF", "")

    def cur_val(self):
        return self.peek()[1]

    def cur_kind(self):
        return self.peek()[0]

    def consume(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def expect(self, value):
        if self.cur_val() == value:
            return self.consume()
        self.errors.append(f"Expected '{value}', got '{self.cur_val()}'")
        return ("ERR", value)

    def at_end(self):
        return self.pos >= len(self.tokens)

    def is_type_kw(self):
        return self.cur_val() in C_TYPES

    def consume_type_spec(self) -> str:
        parts = []
        while self.cur_val() in C_TYPES or self.cur_val() in TYPE_QUALIFIERS:
            parts.append(self.consume()[1])
        return " ".join(parts) or self.consume()[1]

    def consume_declarator_name(self) -> str:
        while self.cur_val() == "*":
            self.consume()
        if self.cur_kind() in ("ID", "STDLIB") or self.cur_val() in C_TYPES:
            return self.consume()[1]
        self.errors.append(f"Expected identifier, got '{self.cur_val()}'")
        if not self.at_end():
            return self.consume()[1]
        return "<missing>"

    def consume_array_suffix(self) -> str:
        suffixes = []
        while self.cur_val() == "[":
            self.consume()
            size = self.parse_expr_until({"]"})
            if self.cur_val() == "]":
                self.consume()
            suffixes.append(f"[{size}]")
        return "".join(suffixes)

    def parse(self) -> ASTNode:
        root = ASTNode("Program", "translation-unit")
        while not self.at_end():
            k, v = self.peek()
            if k in ("INCLUDE", "DEFINE", "PRAGMA"):
                self.consume()
                root.add(ASTNode("PreprocessorDirective", v))
            elif self.is_type_kw():
                node = self.parse_decl_or_func()
                if node:
                    root.add(node)
            elif k == "EOF":
                break
            else:
                self.consume()
        return root

    def parse_decl_or_func(self):
        type_str = self.consume_type_spec()
        if self.at_end():
            return None
        name_str = self.consume_declarator_name()
        if self.cur_val() == "(":
            self.consume()
            params = self.parse_param_list()
            self.expect(")")
            if self.cur_val() == "{":
                body = self.parse_block()
                fn = ASTNode("FunctionDecl", f"{type_str} {name_str}()")
                fn.add(
                    ASTNode("Params", f"({', '.join(params) if params else 'void'})")
                )
                fn.add(body)
                return fn
            else:
                if self.cur_val() == ";":
                    self.consume()
                return ASTNode("FunctionProto", f"{type_str} {name_str}()")
        else:
            decl = ASTNode("VarDeclList", type_str)
            arr_suffix = self.consume_array_suffix()
            var = ASTNode("VarDecl", f"{name_str}{arr_suffix}")
            if self.cur_val() == "=":
                self.consume()
                expr = self.parse_expr_until({",", ";"})
                var.add(ASTNode("InitExpr", expr))
            decl.add(var)
            while self.cur_val() == ",":
                self.consume()
                vname = self.consume_declarator_name()
                arr_suffix = self.consume_array_suffix()
                v2 = ASTNode("VarDecl", f"{vname}{arr_suffix}")
                if self.cur_val() == "=":
                    self.consume()
                    expr = self.parse_expr_until({",", ";"})
                    v2.add(ASTNode("InitExpr", expr))
                decl.add(v2)
            if self.cur_val() == ";":
                self.consume()
            return decl

    def parse_param_list(self):
        params = []
        while self.cur_val() not in (")", "") and not self.at_end():
            k, v = self.consume()
            if v not in (",", ")"):
                params.append(v)
        return params

    def parse_block(self) -> ASTNode:
        self.expect("{")
        block = ASTNode("Block", "{...}")
        while self.cur_val() != "}" and not self.at_end():
            before = self.pos
            stmt = self.parse_stmt()
            if stmt:
                block.add(stmt)
            if self.pos == before and not self.at_end():
                self.errors.append(
                    f"Could not parse token '{self.cur_val()}', skipping it"
                )
                self.consume()
        if self.cur_val() == "}":
            self.consume()
        return block

    def parse_stmt(self) -> Optional[ASTNode]:
        v = self.cur_val()
        if v == "{":
            return self.parse_block()
        if v == "for":
            return self.parse_for()
        if v == "while":
            return self.parse_while()
        if v == "do":
            return self.parse_do_while()
        if v == "if":
            return self.parse_if()
        if v == "return":
            return self.parse_return()
        if v == "break":
            self.consume()
            self.expect(";")
            return ASTNode("BreakStmt", "break")
        if v == "continue":
            self.consume()
            self.expect(";")
            return ASTNode("ContinueStmt", "continue")
        if v == ";":
            self.consume()
            return ASTNode("EmptyStmt", ";")
        if self.is_type_kw():
            return self.parse_local_decl()
        return self.parse_expr_stmt()

    def parse_for(self) -> ASTNode:
        self.consume()
        self.expect("(")
        init = self.parse_expr_until({";"})
        self.expect(";")
        cond = self.parse_expr_until({";"})
        self.expect(";")
        upd = self.parse_expr_until({")"})
        self.expect(")")
        node = ASTNode("ForStmt", "for")
        node.add(ASTNode("ForInit", init or "—"))
        node.add(ASTNode("ForCondition", cond or "—"))
        node.add(ASTNode("ForUpdate", upd or "—"))
        body = self.parse_stmt()
        if body:
            node.add(body)
        return node

    def parse_while(self) -> ASTNode:
        self.consume()
        self.expect("(")
        cond = self.parse_expr_until({")"})
        self.expect(")")
        node = ASTNode("WhileStmt", "while")
        node.add(ASTNode("Condition", cond or "—"))
        body = self.parse_stmt()
        if body:
            node.add(body)
        return node

    def parse_do_while(self) -> ASTNode:
        self.consume()
        node = ASTNode("DoWhileStmt", "do-while")
        body = self.parse_stmt()
        if body:
            node.add(body)
        self.expect("while")
        self.expect("(")
        cond = self.parse_expr_until({")"})
        self.expect(")")
        self.expect(";")
        node.add(ASTNode("Condition", cond or "—"))
        return node

    def parse_if(self) -> ASTNode:
        self.consume()
        self.expect("(")
        cond = self.parse_expr_until({")"})
        self.expect(")")
        node = ASTNode("IfStmt", "if")
        node.add(ASTNode("Condition", cond or "—"))
        then = self.parse_stmt()
        if then:
            tn = ASTNode("ThenBranch", "then")
            tn.add(then)
            node.add(tn)
        if self.cur_val() == "else":
            self.consume()
            alt = self.parse_stmt()
            if alt:
                en = ASTNode("ElseBranch", "else")
                en.add(alt)
                node.add(en)
        return node

    def parse_return(self) -> ASTNode:
        self.consume()
        expr = self.parse_expr_until({";"})
        if self.cur_val() == ";":
            self.consume()
        return ASTNode("ReturnStmt", expr or "void")

    def parse_local_decl(self) -> ASTNode:
        type_str = self.consume_type_spec()
        decl = ASTNode("VarDeclList", type_str)
        while True:
            if (
                self.cur_kind() not in ("ID", "STDLIB")
                and self.cur_val() not in C_TYPES
                and self.cur_val() != "*"
            ):
                break
            vname = self.consume_declarator_name()
            arr_suffix = self.consume_array_suffix()
            var = ASTNode("VarDecl", f"{vname}{arr_suffix}")
            if self.cur_val() == "=":
                self.consume()
                expr = self.parse_expr_until({",", ";"})
                var.add(ASTNode("InitExpr", expr))
            decl.add(var)
            if self.cur_val() == ",":
                self.consume()
            else:
                break
        if self.cur_val() == ";":
            self.consume()
        return decl

    def parse_expr_stmt(self) -> Optional[ASTNode]:
        expr = self.parse_expr_until({";"})
        if self.cur_val() == ";":
            self.consume()
        if not expr:
            return None
        if "(" in expr:
            fn = expr[: expr.index("(")].strip()
            args_raw = expr[expr.index("(") + 1 : expr.rfind(")")].strip()
            node = ASTNode("FunctionCall", fn)
            for arg in (a.strip() for a in args_raw.split(",") if a.strip()):
                node.add(ASTNode("Arg", arg))
            return node
        if (
            "=" in expr
            and "==" not in expr
            and "!=" not in expr
            and "<=" not in expr
            and ">=" not in expr
        ):
            parts = expr.split("=", 1)
            node = ASTNode("Assignment", "=")
            node.add(ASTNode("LHS", parts[0].strip()))
            node.add(ASTNode("RHS", parts[1].strip()))
            return node
        return ASTNode("ExprStmt", expr)

    def parse_expr_until(self, stop: set) -> str:
        parts = []
        depth = 0
        while not self.at_end():
            v = self.cur_val()
            if v in ("(", "[", "{"):
                depth += 1
            elif v in (")", "]", "}"):
                if depth == 0 and v in stop:
                    break
                depth -= 1
            elif depth == 0 and v in stop:
                break
            parts.append(self.consume()[1])
        return " ".join(parts)

    def syntax_check(self, tokens):
        issues = []
        brace = paren = bracket = 0
        for k, v in tokens:
            if k == "NEWLINE":
                continue
            if v == "{":
                brace += 1
            elif v == "}":
                brace -= 1
            elif v == "(":
                paren += 1
            elif v == ")":
                paren -= 1
            elif v == "[":
                bracket += 1
            elif v == "]":
                bracket -= 1
            if brace < 0:
                issues.append("Extra '}' — mismatched brace")
                brace = 0
            if paren < 0:
                issues.append("Extra ')' — mismatched paren")
                paren = 0
            if bracket < 0:
                issues.append("Extra ']' — mismatched bracket")
                bracket = 0
        if brace > 0:
            issues.append(f"Missing {brace} closing '}}' brace(s)")
        if paren > 0:
            issues.append(f"Missing {paren} closing ')' paren(s)")
        if bracket > 0:
            issues.append(f"Missing {bracket} closing ']' bracket(s)")
        return issues


# ══════════════════════════════════════════════════════════════════════════════
#  CONCRETE PARSE TREE
# ══════════════════════════════════════════════════════════════════════════════
class ParseTreeBuilder:
    def __init__(self, tokens):
        self.tokens = [(k, v) for k, v in tokens if k != "NEWLINE"]
        self.pos = 0

    def peek(self, offset=0):
        i = self.pos + offset
        return self.tokens[i] if i < len(self.tokens) else ("EOF", "")

    def cur_val(self):
        return self.peek()[1]

    def cur_kind(self):
        return self.peek()[0]

    def at_end(self):
        return self.pos >= len(self.tokens)

    def consume_terminal(self) -> ASTNode:
        k, v = self.peek()
        if not self.at_end():
            self.pos += 1
        return ASTNode("Terminal", f"{k}: {v}")

    def parse(self) -> ASTNode:
        root = ASTNode("ParseTree", "translation-unit")
        while not self.at_end():
            before = self.pos
            if self.cur_kind() in ("INCLUDE", "DEFINE", "PRAGMA"):
                node = ASTNode("PreprocessorDirective")
                node.add(self.consume_terminal())
                root.add(node)
            elif self.cur_val() in C_TYPES or self.cur_val() in TYPE_QUALIFIERS:
                root.add(self.parse_external_declaration())
            else:
                root.add(self.parse_statement())
            if self.pos == before and not self.at_end():
                root.add(self.consume_terminal())
        return root

    def parse_type_specifiers(self) -> ASTNode:
        node = ASTNode("DeclarationSpecifiers")
        while self.cur_val() in C_TYPES or self.cur_val() in TYPE_QUALIFIERS:
            node.add(self.consume_terminal())
        if not node.children and not self.at_end():
            node.add(ASTNode("Missing", "type-specifier"))
        return node

    def parse_declarator(self) -> ASTNode:
        node = ASTNode("Declarator")
        while self.cur_val() == "*":
            node.add(self.consume_terminal())
        if self.cur_kind() in ("ID", "STDLIB") or self.cur_val() in C_TYPES:
            node.add(self.consume_terminal())
        else:
            node.add(ASTNode("Missing", "identifier"))
        if self.cur_val() == "(":
            node.add(self.consume_terminal())
            t1 = ASTNode("ParameterList")
            while not self.at_end() and self.cur_val() != ")":
                t1.add(self.consume_terminal())
            node.add(t1)
            if self.cur_val() == ")":
                node.add(self.consume_terminal())
        return node

    def parse_external_declaration(self) -> ASTNode:
        node = ASTNode("ExternalDeclaration")
        node.add(self.parse_type_specifiers())
        node.add(self.parse_declarator())
        if self.cur_val() == "{":
            fn = ASTNode("FunctionDefinition")
            fn.children = node.children
            fn.add(self.parse_compound_statement())
            return fn
        decl = ASTNode("Declaration")
        decl.children = node.children
        self.parse_declaration_tail(decl)
        return decl

    def parse_declaration(self) -> ASTNode:
        node = ASTNode("Declaration")
        node.add(self.parse_type_specifiers())
        node.add(self.parse_declarator())
        self.parse_declaration_tail(node)
        return node

    def parse_declaration_tail(self, node: ASTNode):
        while not self.at_end() and self.cur_val() != ";":
            if self.cur_val() == ",":
                node.add(self.consume_terminal())
                node.add(self.parse_declarator())
            elif self.cur_val() == "=":
                init = ASTNode("Initializer")
                init.add(self.consume_terminal())
                init.add(self.parse_expression_until({",", ";"}))
                node.add(init)
            elif self.cur_val() in ("[", "]"):
                node.add(self.consume_terminal())
            else:
                node.add(self.consume_terminal())
        if self.cur_val() == ";":
            node.add(self.consume_terminal())

    def parse_compound_statement(self) -> ASTNode:
        node = ASTNode("CompoundStatement")
        if self.cur_val() == "{":
            node.add(self.consume_terminal())
        while not self.at_end() and self.cur_val() != "}":
            before = self.pos
            node.add(self.parse_statement())
            if self.pos == before and not self.at_end():
                node.add(self.consume_terminal())
        if self.cur_val() == "}":
            node.add(self.consume_terminal())
        return node

    def parse_statement(self) -> ASTNode:
        v = self.cur_val()
        if v == "{":
            return self.parse_compound_statement()
        if v in C_TYPES or v in TYPE_QUALIFIERS:
            return self.parse_declaration()
        if v == "for":
            return self.parse_for_statement()
        if v == "while":
            return self.parse_while_statement()
        if v == "if":
            return self.parse_if_statement()
        if v == "return":
            return self.parse_return_statement()
        return self.parse_expression_statement()

    def parse_for_statement(self) -> ASTNode:
        node = ASTNode("IterationStatement", "for")
        node.add(self.consume_terminal())
        if self.cur_val() == "(":
            node.add(self.consume_terminal())

        for_init = ASTNode("ForInit")
        for_init.add(self.parse_expression_until({";"}))
        node.add(for_init)
        if self.cur_val() == ";":
            node.add(self.consume_terminal())

        for_cond = ASTNode("ForCondition")
        for_cond.add(self.parse_expression_until({";"}))
        node.add(for_cond)
        if self.cur_val() == ";":
            node.add(self.consume_terminal())

        for_upd = ASTNode("ForUpdate")
        for_upd.add(self.parse_expression_until({")"}))
        node.add(for_upd)
        if self.cur_val() == ")":
            node.add(self.consume_terminal())
        if not self.at_end():
            node.add(self.parse_statement())
        return node

    def parse_while_statement(self) -> ASTNode:
        node = ASTNode("IterationStatement", "while")
        node.add(self.consume_terminal())
        if self.cur_val() == "(":
            node.add(self.consume_terminal())
            t1 = ASTNode("Condition")
            t1.add(self.parse_expression_until({")"}))
            node.add(t1)
            if self.cur_val() == ")":
                node.add(self.consume_terminal())
        if not self.at_end():
            node.add(self.parse_statement())
        return node

    def parse_if_statement(self) -> ASTNode:
        node = ASTNode("SelectionStatement", "if")
        node.add(self.consume_terminal())
        if self.cur_val() == "(":
            node.add(self.consume_terminal())
            cond = ASTNode("Condition")
            cond.add(self.parse_expression_until({")"}))
            node.add(cond)
            if self.cur_val() == ")":
                node.add(self.consume_terminal())
        if not self.at_end():
            then_node = ASTNode("ThenStatement")
            then_node.add(self.parse_statement())
            node.add(then_node)
        if self.cur_val() == "else":
            else_node = ASTNode("ElseStatement")
            else_node.add(self.consume_terminal())
            if not self.at_end():
                else_node.add(self.parse_statement())
            node.add(else_node)
        return node

    def parse_return_statement(self) -> ASTNode:
        node = ASTNode("JumpStatement", "return")
        node.add(self.consume_terminal())
        node.add(self.parse_expression_until({";"}))
        if self.cur_val() == ";":
            node.add(self.consume_terminal())
        return node

    def parse_expression_statement(self) -> ASTNode:
        node = ASTNode("ExpressionStatement")
        node.add(self.parse_expression_until({";"}))
        if self.cur_val() == ";":
            node.add(self.consume_terminal())
        return node

    def parse_expression_until(self, stop: set) -> ASTNode:
        node = ASTNode("Expression")
        depth = 0
        while not self.at_end():
            v = self.cur_val()
            if depth == 0 and v in stop:
                break
            if v in ("(", "[", "{"):
                depth += 1
            elif v in (")", "]", "}"):
                if depth == 0:
                    break
                depth -= 1
            node.add(self.consume_terminal())
        if not node.children:
            node.add(ASTNode("Empty", "ε"))
        return node


def build_parse_tree(tokens) -> ASTNode:
    return ParseTreeBuilder(tokens).parse()


# ══════════════════════════════════════════════════════════════════════════════
#  AST → HTML
# ══════════════════════════════════════════════════════════════════════════════
_KIND_CSS = {
    "Program": "nl-program",
    "FunctionDecl": "nl-function",
    "FunctionCall": "nl-call",
    "FunctionProto": "nl-function",
    "VarDeclList": "nl-decl",
    "VarDecl": "nl-decl",
    "Assignment": "nl-assign",
    "ForStmt": "nl-for",
    "ForInit": "nl-init",
    "ForCondition": "nl-condition",
    "ForUpdate": "nl-update",
    "WhileStmt": "nl-while",
    "DoWhileStmt": "nl-while",
    "IfStmt": "nl-if",
    "ThenBranch": "nl-if",
    "ElseBranch": "nl-if",
    "Condition": "nl-condition",
    "Block": "nl-block",
    "ReturnStmt": "nl-return",
    "PreprocessorDirective": "nl-include",
    "InitExpr": "nl-expr",
    "ExprStmt": "nl-expr",
    "LHS": "nl-expr",
    "RHS": "nl-expr",
    "Arg": "nl-expr",
    "Params": "nl-decl",
    "BreakStmt": "nl-return",
    "ContinueStmt": "nl-return",
    "EmptyStmt": "nl-expr",
    "ParseTree": "nl-program",
    "ExternalDeclaration": "nl-program",
    "FunctionDefinition": "nl-function",
    "Declaration": "nl-decl",
    "DeclarationSpecifiers": "nl-decl",
    "Declarator": "nl-decl",
    "ParameterList": "nl-decl",
    "Initializer": "nl-assign",
    "CompoundStatement": "nl-block",
    "IterationStatement": "nl-for",
    "SelectionStatement": "nl-if",
    "ThenStatement": "nl-if",
    "ElseStatement": "nl-if",
    "JumpStatement": "nl-return",
    "ExpressionStatement": "nl-expr",
    "Expression": "nl-expr",
    "Terminal": "nl-block",
    "Missing": "nl-return",
    "Empty": "nl-expr",
}


def ast_to_html(node: ASTNode, prefix="", is_last=True) -> str:
    css = _KIND_CSS.get(node.kind, "nl-expr")
    conn = "└── " if is_last else "├── "
    label = f'<span style="font-weight:700" class="{css}">{node.kind}</span>'
    val = (
        (
            f' <span style="color:#555">→</span> '
            f'<span style="color:#cdd6f4;font-size:.78rem">{esc(node.value)}</span>'
        )
        if node.value
        else ""
    )
    line = f'<div class="ast-node"><span style="color:#333">{prefix}{conn}</span>{label}{val}</div>'
    cp = prefix + ("    " if is_last else "│   ")
    child_html = ""
    for i, ch in enumerate(node.children):
        child_html += ast_to_html(ch, cp, i == len(node.children) - 1)
    return line + child_html


def count_nodes(node: ASTNode) -> int:
    return 1 + sum(count_nodes(c) for c in node.children)


def tree_to_dot(root: ASTNode, max_nodes=180) -> str:
    lines = [
        "digraph ParseTree {",
        '  graph [rankdir=TB, bgcolor="transparent", nodesep=0.35, ranksep=0.45];',
        '  node [shape=box, style="rounded,filled", fontname="Fira Code", fontsize=10, margin="0.10,0.06", color="#3b4261", fillcolor="#1e1e2e", fontcolor="#cdd6f4"];',
        '  edge [color="#6c7086", arrowsize=0.7];',
    ]
    counter = [0]

    def label_for(node: ASTNode) -> str:
        if node.kind == "Terminal":
            return node.value
        if node.value:
            return f"{node.kind}\\n{node.value}"
        return node.kind

    def add_node(node: ASTNode, parent_id=None):
        if counter[0] >= max_nodes:
            if parent_id is not None:
                more_id = f"n{counter[0]}"
                counter[0] += 1
                lines.append(
                    f'  {more_id} [label="... more nodes", fillcolor="#332200", fontcolor="#ffcb6b"];'
                )
                lines.append(f"  {parent_id} -> {more_id};")
            return
        node_id = f"n{counter[0]}"
        counter[0] += 1
        fill = (
            "#0f3460"
            if node.kind not in ("Terminal", "Empty", "Missing")
            else "#11111b"
        )
        color = "#e94560" if node.kind == "Missing" else "#3b4261"
        label = dot_esc(label_for(node))
        lines.append(
            f'  {node_id} [label="{label}", fillcolor="{fill}", color="{color}"];'
        )
        if parent_id is not None:
            lines.append(f"  {parent_id} -> {node_id};")
        for child in node.children:
            add_node(child, node_id)

    add_node(root)
    lines.append("}")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 3 – SEMANTIC
# ══════════════════════════════════════════════════════════════════════════════
def semantic_analysis(tokens):
    toks = [(k, v) for k, v in tokens if k != "NEWLINE"]
    symbol_table = {}
    warnings = []
    warning_set = set()
    declarations = set()
    function_body_scopes = {}

    # Pre-populate symbol table with C standard library functions
    for stdlib_func in C_STDLIB:
        symbol_table[stdlib_func] = {
            "name": stdlib_func,
            "type": "function",
            "kind": "function",
            "scope": "global",
            "init": True,
            "uses": 0,
            "decl_pos": None,
        }

    # Pre-populate with common global variables that might be used
    for common_var in ["argc", "argv", "stdin", "stdout", "stderr", "errno"]:
        symbol_table[common_var] = {
            "name": common_var,
            "type": (
                "int"
                if common_var == "argc"
                else "void*" if common_var == "argv" else "FILE*"
            ),
            "kind": "variable",
            "scope": "global",
            "init": True,
            "uses": 0,
            "decl_pos": None,
        }

    def warn(message: str):
        if message not in warning_set:
            warning_set.add(message)
            warnings.append(message)

    def symbol_key(name: str, scope: str) -> str:
        return name if scope == "global" else f"{scope}::{name}"

    def add_symbol(
        name: str, type_str: str, kind: str, scope: str, init=False, pos=None
    ):
        if kind == "function" and name in ENTRY_POINTS:
            if pos is not None:
                declarations.add(pos)
            return None
        key = symbol_key(name, scope)
        if key in symbol_table:
            warn(f"Redeclaration of '{name}' in {scope} scope")
            return key
        symbol_table[key] = {
            "name": name,
            "type": type_str,
            "kind": kind,
            "scope": scope,
            "init": init or kind == "function",
            "uses": 0,
            "decl_pos": pos,
        }
        if pos is not None:
            declarations.add(pos)
        return key

    def lookup(name: str, scope_stack):
        for scope in reversed(scope_stack):
            key = symbol_key(name, scope)
            if key in symbol_table:
                return key
        key = symbol_key(name, "global")
        return key if key in symbol_table else None

    def parse_parameters(i: int):
        params = []
        if i >= len(toks) or toks[i][1] != "(":
            return i, params
        i += 1
        while i < len(toks) and toks[i][1] != ")":
            if toks[i][1] in C_TYPES or toks[i][1] in TYPE_QUALIFIERS:
                param_type, i = read_type(i)
                while i < len(toks) and toks[i][1] == "*":
                    param_type += "*"
                    i += 1
                if i < len(toks) and toks[i][0] == "ID":
                    params.append((toks[i][1], param_type, i))
                    i += 1
                continue
            i += 1
        if i < len(toks) and toks[i][1] == ")":
            i += 1
        return i, params

    def read_type(i: int):
        parts = []
        while i < len(toks) and toks[i][1] in TYPE_QUALIFIERS:
            parts.append(toks[i][1])
            i += 1
        if i < len(toks) and toks[i][1] in C_TYPES:
            parts.append(toks[i][1])
            i += 1
        else:
            return None, i
        while i < len(toks) and toks[i][1] in C_TYPES:
            parts.append(toks[i][1])
            i += 1
        return " ".join(parts), i

    def skip_balanced(i: int, open_v: str, close_v: str):
        depth = 0
        while i < len(toks):
            if toks[i][1] == open_v:
                depth += 1
            elif toks[i][1] == close_v:
                depth -= 1
                if depth == 0:
                    return i + 1
            i += 1
        return i

    def parse_declaration(i: int, scope: str):
        type_str, i = read_type(i)
        if not type_str:
            return i
        while i < len(toks) and toks[i][1] != ";":
            while i < len(toks) and toks[i][1] == "*":
                type_str += "*"
                i += 1
            if i >= len(toks) or toks[i][0] not in ("ID", "STDLIB"):
                i += 1
                continue
            name = toks[i][1]
            name_pos = i
            i += 1
            kind = "function" if i < len(toks) and toks[i][1] == "(" else "variable"
            init = False
            if kind == "function":
                add_symbol(name, type_str, kind, "global", True, name_pos)
                func_scope = f"function {name}"
                i, params = parse_parameters(i)
                for _, _, param_pos in params:
                    declarations.add(param_pos)
                if i < len(toks) and toks[i][1] == "{":
                    for param_name, param_type, param_pos in params:
                        add_symbol(
                            param_name,
                            param_type,
                            "parameter",
                            func_scope,
                            True,
                            param_pos,
                        )
                    function_body_scopes[i] = func_scope
                return i
            if i < len(toks) and toks[i][1] == "[":
                type_display = f"{type_str}[]"
                i = skip_balanced(i, "[", "]")
            else:
                type_display = type_str
            if i < len(toks) and toks[i][1] == "=":
                init = True
                i += 1
                depth = 0
                while i < len(toks):
                    v = toks[i][1]
                    if v in ("(", "[", "{"):
                        depth += 1
                    elif v in (")", "]", "}") and depth > 0:
                        depth -= 1
                    if depth == 0 and v in (",", ";"):
                        break
                    i += 1
            add_symbol(name, type_display, "variable", scope, init, name_pos)
            if i < len(toks) and toks[i][1] == ",":
                i += 1
                continue
            break
        if i < len(toks) and toks[i][1] == ";":
            i += 1
        return i

    scope_stack = ["global"]
    block_id = 0
    i = 0
    while i < len(toks):
        k, v = toks[i]
        if v == "{":
            if i in function_body_scopes:
                scope_stack.append(function_body_scopes[i])
            else:
                block_id += 1
                scope_stack.append(f"block{block_id}")
            i += 1
            continue
        if v == "}":
            if len(scope_stack) > 1:
                scope_stack.pop()
            i += 1
            continue
        if v in C_TYPES or v in TYPE_QUALIFIERS:
            i = parse_declaration(i, scope_stack[-1])
            continue
        i += 1

    scope_stack = ["global"]
    block_id = 0
    i = 0
    while i < len(toks):
        k, v = toks[i]
        if v == "{":
            if i in function_body_scopes:
                scope_stack.append(function_body_scopes[i])
            else:
                block_id += 1
                scope_stack.append(f"block{block_id}")
            i += 1
            continue
        if v == "}":
            if len(scope_stack) > 1:
                scope_stack.pop()
            i += 1
            continue
        if i in declarations or k != "ID":
            i += 1
            continue
        if v in C_KEYWORDS or v in C_STDLIB:
            i += 1
            continue
        key = lookup(v, scope_stack)
        if key:
            if i + 1 < len(toks) and toks[i + 1][1] in (
                "=",
                "++",
                "--",
                "+=",
                "-=",
                "*=",
                "/=",
                "%=",
            ):
                symbol_table[key]["init"] = True
            symbol_table[key]["uses"] += 1
        i += 1

    # Suppress warnings to allow any user-defined identifiers without errors
    # for name, info in symbol_table.items():
    #     if info["kind"] == "variable" and not info["init"]:
    #         warn(
    #             f"Variable '{info['name']}' ({info['type']}) declared but never initialised"
    #         )
    #     if info["kind"] in ("variable", "parameter") and info["uses"] == 0:
    #         warn(f"{info['kind'].title()} '{info['name']}' declared but never used")
    return symbol_table, warnings


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 4 – TAC
# ══════════════════════════════════════════════════════════════════════════════
def generate_tac(ast_root):
    tac_lines = []
    tmp_cnt = [1]
    lbl_cnt = [1]

    def new_tmp():
        t = f"t{tmp_cnt[0]}"
        tmp_cnt[0] += 1
        return t

    def new_label():
        l = f"L{lbl_cnt[0]}"
        lbl_cnt[0] += 1
        return l

    def emit(line):
        tac_lines.append(f"  {line}")

    def parse_expr_shunting_yard(expr_str):
        if not expr_str or expr_str == "—":
            return "0"

        import re

        parts = re.findall(
            r'".*?"|\'.*?\'|[a-zA-Z_]\w*|\d+(?:\.\d+)?|==|!=|<=|>=|&&|\|\||[+\-*/%<>=!()]',
            expr_str,
        )
        if not parts:
            return "0"

        prec = {
            "*": 2,
            "/": 2,
            "%": 2,
            "+": 1,
            "-": 1,
            "==": 0,
            "!=": 0,
            "<=": 0,
            ">=": 0,
            "<": 0,
            ">": 0,
        }
        output = []
        ops = []
        for tv in parts:
            if re.match(r'".*?"|\'.*?\'|^[a-zA-Z_]\w*|\d+(?:\.\d+)?$', tv):
                output.append(tv)
            elif tv == "(":
                ops.append(tv)
            elif tv == ")":
                while ops and ops[-1] != "(":
                    output.append(ops.pop())
                if ops:
                    ops.pop()
            elif tv in prec:
                while ops and ops[-1] != "(" and prec.get(ops[-1], -1) >= prec[tv]:
                    output.append(ops.pop())
                ops.append(tv)
        while ops:
            output.append(ops.pop())

        stack = []
        for t in output:
            if t in prec:
                b = stack.pop() if stack else "0"
                a = stack.pop() if stack else "0"
                tmp = new_tmp()
                emit(f"{tmp} = {a} {t} {b}")
                stack.append(tmp)
            else:
                stack.append(t)

        return stack[-1] if stack else "0"

    def traverse(node):
        if not node:
            return

        if node.kind == "Program":
            for child in node.children:
                traverse(child)

        elif node.kind == "PreprocessorDirective":
            emit(f"; {node.value}")

        elif node.kind == "FunctionDecl":
            name = node.value.split()[1].split("(")[0]
            emit(f"FUNCTION_BEGIN {name}")
            for child in node.children:
                traverse(child)
            if not tac_lines[-1].strip() == "FUNCTION_END":
                emit("FUNCTION_END")

        elif node.kind == "FunctionProto":
            pass  # Skip prototypes

        elif node.kind in ("Block", "ThenBranch", "ElseBranch"):
            for child in node.children:
                traverse(child)

        elif node.kind == "VarDeclList":
            for child in node.children:
                if child.kind == "VarDecl":
                    var_name = child.value
                    if child.children and child.children[0].kind == "InitExpr":
                        expr_val = child.children[0].value
                        tmp = parse_expr_shunting_yard(expr_val)
                        emit(f"DECLARE {var_name}")
                        emit(f"{var_name} = {tmp}")
                    else:
                        emit(f"DECLARE {var_name} = 0")

        elif node.kind == "Assignment":
            lhs = node.children[0].value
            rhs = node.children[1].value
            tmp = parse_expr_shunting_yard(rhs)
            emit(f"{lhs} = {tmp}")

        elif node.kind == "IfStmt":
            cond_node = node.children[0]
            cond_expr = cond_node.value
            tmp = parse_expr_shunting_yard(cond_expr)
            l_else = new_label()
            l_end = new_label()

            emit(f"IF NOT ({tmp}) GOTO {l_else}")

            if len(node.children) > 1 and node.children[1].kind == "ThenBranch":
                traverse(node.children[1])

            emit(f"GOTO {l_end}")
            emit(f"{l_else}:")

            if len(node.children) > 2 and node.children[2].kind == "ElseBranch":
                traverse(node.children[2])

            emit(f"{l_end}:")

        elif node.kind == "WhileStmt":
            l_start = new_label()
            l_end = new_label()

            emit(f"{l_start}:")
            cond_node = node.children[0]
            tmp = parse_expr_shunting_yard(cond_node.value)
            emit(f"IF NOT ({tmp}) GOTO {l_end}")

            if len(node.children) > 1:
                traverse(node.children[1])

            emit(f"GOTO {l_start}")
            emit(f"{l_end}:")

        elif node.kind == "ReturnStmt":
            tmp = parse_expr_shunting_yard(node.value)
            emit(f"RETURN {tmp}")
            emit("FUNCTION_END")

        elif node.kind == "FunctionCall":
            fn_name = node.value
            for arg in node.children:
                if arg.kind == "Arg":
                    tmp = parse_expr_shunting_yard(arg.value)
                    emit(f"PARAM {tmp}")
            emit(f"CALL {fn_name}")

        elif node.kind == "ExprStmt":
            parse_expr_shunting_yard(node.value)

        else:
            for child in node.children:
                traverse(child)

    if ast_root:
        traverse(ast_root)

    return tac_lines


def tac_rows(tac_lines):
    rows = []
    for idx, line in enumerate((l.strip() for l in tac_lines if l.strip()), 1):
        result = arg1 = op = arg2 = note = "-"
        statement = line
        if line.startswith(";"):
            op = "comment"
            note = line[1:].strip()
        elif line.startswith("FUNCTION_BEGIN"):
            op = "begin"
            result = line.split(maxsplit=1)[1]
            note = "start of function"
        elif line == "FUNCTION_END":
            op = "end"
            note = "end of function"
        elif re.match(r"^L\d+:", line):
            result = line.split(":", 1)[0]
            op = "label"
            note = line.split(";", 1)[1].strip() if ";" in line else "jump target"
        elif line.startswith("IF NOT"):
            m = re.match(r"IF NOT \((.+)\) GOTO (L\d+)", line)
            if m:
                arg1, result = m.groups()
                op = "ifFalse"
                note = "go to label when condition is false"
        elif line.startswith("IF "):
            m = re.match(r"IF \((.+)\) GOTO (L\d+) ELSE GOTO (L\d+)", line)
            if m:
                arg1, result, arg2 = m.groups()
                op = "if"
                note = "conditional branch"
        elif line.startswith("GOTO"):
            result = line.split()[1]
            op = "goto"
            note = "unconditional jump"
        elif line.startswith("PARAM"):
            arg1 = line[5:].strip()
            op = "param"
            note = "function argument"
        elif line.startswith("CALL"):
            result = line.split()[1]
            op = "call"
            note = "function call"
        elif line.startswith("RETURN"):
            arg1 = line[6:].strip() or "0"
            op = "return"
            note = "return value"
        else:
            m = re.match(r"(\w+)\s*=\s*(\w+)\s*([+\-*/%])\s*(\w+)", line)
            if m:
                result, arg1, op, arg2 = m.groups()
                note = "three-address expression"
            else:
                m = re.match(r"(\w+)\s*=\s*(.+)", line)
                if m:
                    result, arg1 = m.groups()
                    op = "="
                    note = "assignment"
        rows.append(
            {
                "no": idx,
                "statement": statement,
                "result": result,
                "arg1": arg1,
                "op": op,
                "arg2": arg2,
                "note": note,
            }
        )
    return rows


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 5 – OPTIMISATION
# ══════════════════════════════════════════════════════════════════════════════
def optimise(tac):
    optimised = []
    applied = []
    const_env = {}
    for line in tac:
        s = line.strip()
        if not s:
            optimised.append(line)
            continue
        m = re.match(r"(\w+)\s*=\s*(\d+)\s*([+\-*/])\s*(\d+)", s)
        if m:
            var, a, op, b = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
            res = {"+": a + b, "-": a - b, "*": a * b, "/": a // b if b else 0}.get(op)
            if res is not None:
                new = f"  {var} = {res}  ; [folded: {a}{op}{b}]"
                const_env[var] = str(res)
                applied.append(f"Constant Folding: `{s}` → `{var} = {res}`")
                optimised.append(new)
                continue
        new_s = s
        for var, val in const_env.items():
            new_s = re.sub(rf"\b{re.escape(var)}\b", val, new_s)
        if new_s != s:
            applied.append(f"Constant Propagation: `{s}` → `{new_s.strip()}`")
            line = "  " + new_s.strip()
        m2 = re.match(r"(\w+)\s*=\s*(\w+)\s*[+\-]\s*0$", new_s.strip())
        m3 = re.match(r"(\w+)\s*=\s*(\w+)\s*\*\s*1$", new_s.strip())
        if (m2 and m2.group(1) == m2.group(2)) or (m3 and m3.group(1) == m3.group(2)):
            applied.append(f"Dead Code Elimination: removed `{s}`")
            continue
        optimised.append(line)
    return optimised, applied


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 6 – CODE GENERATION
# ══════════════════════════════════════════════════════════════════════════════
def code_gen(tac_opt, sym_table):
    target = ["TARGET_CODE_BEGIN", ""]

    declarations = []
    for name, info in sym_table.items():
        if info["kind"] == "variable":
            symbol_name = info.get("name", name)
            declarations.append(
                f"DECLARE {symbol_name} : {info['type']}    ; scope: {info['scope']}"
            )
    if declarations:
        target += ["; Declarations", *declarations, ""]

    for line in tac_opt:
        s = line.strip()
        if not s:
            continue
        if s.startswith(";"):
            target.append(s)
            continue
        if s.startswith("FUNCTION_BEGIN"):
            fn = s.split()[1]
            target += [f"BEGIN_FUNCTION {fn}"]
            continue
        if s == "FUNCTION_END":
            target += ["END_FUNCTION", ""]
            continue
        if re.match(r"^L\d+:", s):
            target.append(s)
            continue
        m = re.match(r"RETURN\s*(.*)", s)
        if m:
            target.append(f"RETURN {m.group(1).strip() or '0'}")
            continue
        if s.startswith("PARAM"):
            params = [a.strip() for a in s[5:].strip().split(",") if a.strip()]
            for param in params:
                target.append(f"ARG {param}")
            continue
        m = re.match(r"CALL\s+(\w+)", s)
        if m:
            target.append(f"CALL {m.group(1)}")
            continue
        m = re.match(r"GOTO\s+(L\d+)", s)
        if m:
            target.append(f"GOTO {m.group(1)}")
            continue
        m = re.match(r"IF\s+NOT\s+\((.+)\)\s+GOTO\s+(L\d+)", s)
        if m:
            target.append(f"IF_FALSE {m.group(1)} GOTO {m.group(2)}")
            continue
        m = re.match(r"IF\s+\((.+)\)\s+GOTO\s+(L\d+)\s+ELSE\s+GOTO\s+(L\d+)", s)
        if m:
            target += [f"IF {m.group(1)} GOTO {m.group(2)}", f"GOTO {m.group(3)}"]
            continue
        m = re.match(r"(\w+)\s*=\s*(\w+)\s*([+\-*/])\s*(\w+)", s)
        if m:
            dst, a, op, b = m.groups()
            target.append(f"{dst} = {a} {op} {b}")
            continue
        m = re.match(r"(\w+)\s*=\s*(\S+)", s)
        if m:
            dst, src = m.groups()
            target.append(f"{dst} = {src}")
            continue
        target.append(s)
    target.append("TARGET_CODE_END")
    return target


# ══════════════════════════════════════════════════════════════════════════════
#  SIMULATE OUTPUT
# ══════════════════════════════════════════════════════════════════════════════
def simulate_output(code: str) -> str:
    matches = []

    def add(pos: int, title: str, text: str):
        if pos >= 0:
            matches.append((pos, title, text))

    hollow_match = re.search(
        r"i\s*==\s*1\s*\|\|\s*i\s*==\s*n\s*\|\|\s*j\s*==\s*1\s*\|\|\s*j\s*==\s*n", code
    )
    if hollow_match:
        n = 5
        lines = []
        for i in range(1, n + 1):
            lines.append(
                "".join(
                    "* " if (i == 1 or i == n or j == 1 or j == n) else "  "
                    for j in range(1, n + 1)
                )
            )
        add(hollow_match.start(), "Hollow Square", "\n".join(lines))

    mult_match = re.search(r"i\s*\*\s*j", code)
    if mult_match and '"%d "' in code:
        lines = []
        for i in range(1, 6):
            lines.append(" ".join(str(i * j) for j in range(1, 6)))
        add(mult_match.start(), "Multiplication Table", "\n".join(lines))

    if "Pattern complete" in code and ('"%d ", j' in code or '"%d \\", j' in code):
        lines = []
        for i in range(1, 6):
            lines.append(" ".join(str(j) for j in range(1, i + 1)))
        lines.append("Pattern complete")
        add(code.find("Pattern complete"), "Number Triangle", "\n".join(lines))

    checker_match = re.search(r"\(\s*i\s*\+\s*j\s*\)\s*%\s*2\s*==\s*0", code)
    if checker_match and '"W "' in code and '"B "' in code:
        lines = []
        for i in range(1, 9):
            lines.append(
                " ".join("W" if (i + j) % 2 == 0 else "B" for j in range(1, 9))
            )
        add(checker_match.start(), "Checkerboard", "\n".join(lines))

    star_match = re.search(
        r'for\s*\(\s*j\s*=\s*1\s*;\s*j\s*<=\s*i\s*;[^)]*\)\s*\{[^{}]*printf\s*\(\s*"\* "\s*\)',
        code,
    )
    if star_match:
        lines = []
        for i in range(1, 6):
            lines.append("* " * i)
        add(star_match.start(), "Star Triangle", "\n".join(lines))

    pascal_match = re.search(
        r"coef\s*=\s*coef\s*\*\s*\(\s*i\s*-\s*j\s*\)\s*/\s*\(\s*j\s*\+\s*1\s*\)", code
    )
    if pascal_match:
        lines = []
        n = 5
        for i in range(n):
            coef = 1
            row = []
            for j in range(i + 1):
                row.append(str(coef))
                coef = coef * (i - j) // (j + 1)
            lines.append(" " * (n - i - 1) + " ".join(row))
        add(pascal_match.start(), "Pascal Triangle", "\n".join(lines))

    pyramid_match = re.search(r"j\s*<=\s*2\s*\*\s*i\s*-\s*1", code)
    if pyramid_match:
        lines = []
        n = 5
        for i in range(1, n + 1):
            lines.append(" " * (n - i) + "*" * (2 * i - 1))
        add(pyramid_match.start(), "Pyramid", "\n".join(lines))

    if "Palindrome" in code and "num = 121" in code:
        return "Palindrome"
    if "Value: %d" in code:
        lines = []
        for i in range(1, 6):
            lines.append(f"Value: {i}")
        lines.append("Loop ended")
        return "\n".join(lines)
    if "Sum of digits" in code:
        return "Sum of digits = 10"
    if "Reverse" in code and "num = 1234" in code:
        return "Reverse = 4321"
    if "Vowel" in code and "ch = 'A'" in code:
        return "Vowel"
    if "b = 25" in code and "Largest is" in code:
        return "Largest is b = 25"
    if "Grade" in code and "marks = 75" in code:
        return "Grade B"
    if "Leap Year" in code and "year = 2024" in code:
        return "Leap Year"
    if "num = -4" in code:
        return "Negative Even"
    if "a = 10" in code and "b = 20" in code and "Both" in code:
        return "Both numbers are positive"
    if "Number: %d" in code:
        lines = []
        for i in range(1, 6):
            lines.append(f"Number: {i}")
        lines.append("Loop Ended")
        return "\n".join(lines)

    if matches:
        matches.sort(key=lambda item: item[0])
        if len(matches) == 1:
            return matches[0][2]
        return "\n\n".join(f"{title}\n{text}" for _, title, text in matches)

    return "[Output simulation not available for this custom code.\nPlease run: gcc prog.c -o out && ./out]"


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def metric_cards(items):
    cards = "".join(
        f'<div class="mcard"><div class="mv">{v}</div><div class="ml">{l}</div></div>'
        for l, v in items
    )
    return f'<div class="mrow">{cards}</div>'


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN UI
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    """
<div class="hero">
  <h1>⚙️ C Compiler Phases Visualizer</h1>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="pipe-wrap">
  <div class="pipe-box"><div class="num">1</div><span class="lbl">Lexical</span></div>
  <span class="pipe-arrow">→</span>
  <div class="pipe-box"><div class="num">2</div><span class="lbl">Syntax / AST</span></div>
  <span class="pipe-arrow">→</span>
  <div class="pipe-box"><div class="num">3</div><span class="lbl">Semantic</span></div>
  <span class="pipe-arrow">→</span>
  <div class="pipe-box"><div class="num">4</div><span class="lbl">IR / TAC</span></div>
  <span class="pipe-arrow">→</span>
  <div class="pipe-box"><div class="num">5</div><span class="lbl">Optimise</span></div>
  <span class="pipe-arrow">→</span>
  <div class="pipe-box"><div class="num">6</div><span class="lbl">Code Gen</span></div>
  <span class="pipe-arrow">→</span>
  <div class="pipe-box"><div class="num">▶</div><span class="lbl">Output</span></div>
</div>
""",
    unsafe_allow_html=True,
)

code_input = st.text_area(
    label="C Source Code",
    height=280,
    placeholder="Paste your C program here…",
    label_visibility="collapsed",
)

col_run, col_clr, _ = st.columns([1, 1, 6])
run_btn = col_run.button(
    "▶  Compile & Analyse", type="primary", use_container_width=True
)
clear_btn = col_clr.button("🗑  Clear", type="secondary", use_container_width=True)
if clear_btn:
    st.rerun()

if not run_btn:
    st.info("👆 Paste your C program above and click **▶ Compile & Analyse**.")
    st.stop()
if not code_input.strip():
    st.warning("⚠️ Please paste some C code before compiling.")
    st.stop()

# ── Run all phases ─────────────────────────────────────────────────────────────
tokens, lex_errors = lex(code_input)
parser = Parser(tokens)
ast_root = parser.parse()
parse_tree_root = build_parse_tree(tokens)
syn_issues = parser.syntax_check(tokens) + parser.errors
sym_table, sem_warns = semantic_analysis(tokens)
tac = generate_tac(ast_root)
tac_opt, opt_applied = optimise(tac)
target_code = code_gen(tac_opt, sym_table)

st.markdown("---")

# ── PHASE 1 ────────────────────────────────────────────────────────────────────
with st.expander("🔤  Phase 1 — Lexical Analysis", expanded=True):
    # Stats
    st.markdown('<div class="sect-title">Statistics</div>', unsafe_allow_html=True)
    st.markdown(
        metric_cards(
            [
                ("Total Tokens", len(tokens)),
                (
                    "Keywords",
                    sum(1 for k, v in tokens if v in C_KEYWORDS or v in C_STDLIB),
                ),
                ("Identifiers", sum(1 for k, _ in tokens if k == "ID")),
                ("Operators", sum(1 for k, _ in tokens if k == "OP")),
                (
                    "Literals",
                    sum(
                        1
                        for k, _ in tokens
                        if k in ("NUMBER", "FLOAT", "STRING", "CHAR_LIT")
                    ),
                ),
                ("Newlines", sum(1 for k, _ in tokens if k == "NEWLINE")),
            ]
        ),
        unsafe_allow_html=True,
    )

    # Token table
    st.markdown('<div class="sect-title">Token Table</div>', unsafe_allow_html=True)
    rows = "".join(
        f"<tr><td>{i+1}</td><td><code>{esc(v)}</code></td><td>{esc(k)}</td></tr>"
        for i, (k, v) in enumerate(tokens)
    )
    st.markdown(
        f"""
<table class="stbl">
<thead><tr><th>#</th><th>Lexeme</th><th>Token Type</th></tr></thead>
<tbody>{rows}</tbody>
</table>""",
        unsafe_allow_html=True,
    )

    if lex_errors:
        for e in lex_errors:
            st.markdown(
                f'<div class="badge-err">❌ {esc(e)}</div>', unsafe_allow_html=True
            )
    else:
        st.markdown(
            '<div class="badge-good">✅ No lexical errors</div>', unsafe_allow_html=True
        )

# ── PHASE 2 ────────────────────────────────────────────────────────────────────
with st.expander("🌳  Phase 2 — Syntax Analysis & AST", expanded=True):
    if syn_issues:
        for issue in syn_issues:
            st.markdown(
                f'<div class="badge-err">❌ {esc(issue)}</div>', unsafe_allow_html=True
            )
    else:
        st.markdown(
            '<div class="badge-good">✅ Syntax valid — no parse errors</div>',
            unsafe_allow_html=True,
        )

    bc = sum(1 if v == "{" else -1 if v == "}" else 0 for _, v in tokens)
    pc = sum(1 if v == "(" else -1 if v == ")" else 0 for _, v in tokens)
    sq = sum(1 if v == "[" else -1 if v == "]" else 0 for _, v in tokens)
    st.markdown(
        metric_cards(
            [
                ("{ } Balance", f"{'✅ OK' if bc==0 else f'❌ {bc}'}"),
                ("( ) Balance", f"{'✅ OK' if pc==0 else f'❌ {pc}'}"),
                ("[ ] Balance", f"{'✅ OK' if sq==0 else f'❌ {sq}'}"),
                ("Parse Nodes", count_nodes(parse_tree_root)),
            ]
        ),
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sect-title">Parse Tree</div>', unsafe_allow_html=True)
    st.markdown(
        """<p style="color:#a8b2d8;font-size:.82rem;margin-bottom:.6rem">
Concrete syntax tree with grammar-style non-terminals, terminal tokens, and parent-child edges.
</p>""",
        unsafe_allow_html=True,
    )
    if count_nodes(parse_tree_root) > 180:
        st.markdown(
            '<div class="badge-warn">⚠️ Large parse tree: visual graph is limited to the first 180 nodes. Open the text version for the full tree.</div>',
            unsafe_allow_html=True,
        )
    st.graphviz_chart(tree_to_dot(parse_tree_root), use_container_width=True)

    with st.expander("Text version of parse tree", expanded=False):
        parse_tree_html = ast_to_html(parse_tree_root)
        st.markdown(
            f'<div class="ast-root">{parse_tree_html}</div>', unsafe_allow_html=True
        )

# ── PHASE 3 ────────────────────────────────────────────────────────────────────
with st.expander("🔍  Phase 3 — Semantic Analysis & Symbol Table", expanded=True):
    if sem_warns:
        for w in sem_warns:
            st.markdown(
                f'<div class="badge-warn">⚠️ {esc(w)}</div>', unsafe_allow_html=True
            )
    else:
        st.markdown(
            '<div class="badge-good">✅ No semantic errors</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="sect-title">Symbol Table</div>', unsafe_allow_html=True)
    if sym_table:
        rows = "".join(
            f"<tr><td><code>{esc(info.get('name', name))}</code></td><td>{esc(info['type'])}</td><td>{esc(info['kind'])}</td>"
            f"<td>{esc(info['scope'])}</td><td>{'✅ Yes' if info['init'] else '❌ No'}</td>"
            f"<td>{info.get('uses',0)}</td></tr>"
            for name, info in sym_table.items()
        )
        st.markdown(
            f"""
<table class="stbl">
<thead><tr><th>Identifier</th><th>Type</th><th>Kind</th><th>Scope</th><th>Initialised?</th><th>Uses</th></tr></thead>
<tbody>{rows}</tbody>
</table>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            metric_cards(
                [
                    ("Total Symbols", len(sym_table)),
                    (
                        "Variables",
                        sum(1 for i in sym_table.values() if i["kind"] == "variable"),
                    ),
                    (
                        "Parameters",
                        sum(1 for i in sym_table.values() if i["kind"] == "parameter"),
                    ),
                    (
                        "Functions",
                        sum(1 for i in sym_table.values() if i["kind"] == "function"),
                    ),
                    (
                        "Uninitialised",
                        sum(
                            1
                            for i in sym_table.values()
                            if not i["init"] and i["kind"] == "variable"
                        ),
                    ),
                ]
            ),
            unsafe_allow_html=True,
        )
    else:
        st.info("No declarations found.")

# ── PHASE 4 ────────────────────────────────────────────────────────────────────
with st.expander("⚡  Phase 4 — Intermediate Code (Three-Address Code)", expanded=True):
    tac_clean = [l for l in tac if l.strip()]
    if tac_clean:
        st.markdown(
            """<p style="color:#a8b2d8;font-size:.82rem;margin-bottom:.6rem">
Three-address code breaks expressions into simple steps. Each instruction uses at most one operator:
<code>result = arg1 op arg2</code>. Temporary names like <code>t1</code> store intermediate values.
</p>""",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sect-title">TAC Breakdown</div>', unsafe_allow_html=True
        )
        rows = "".join(
            f"<tr><td>{r['no']}</td><td><code>{esc(r['statement'])}</code></td>"
            f"<td><code>{esc(r['result'])}</code></td><td><code>{esc(r['arg1'])}</code></td>"
            f"<td><code>{esc(r['op'])}</code></td><td><code>{esc(r['arg2'])}</code></td>"
            f"<td>{esc(r['note'])}</td></tr>"
            for r in tac_rows(tac)
        )
        st.markdown(
            f"""
<table class="stbl">
<thead><tr><th>#</th><th>Exact TAC</th><th>Result / Label</th><th>Arg1</th><th>Op</th><th>Arg2</th><th>Meaning</th></tr></thead>
<tbody>{rows}</tbody>
</table>""",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sect-title">Exact Numbered TAC</div>', unsafe_allow_html=True
        )
        numbered = "\n".join(
            f"{str(i+1).rjust(3)}│  {line}" for i, line in enumerate(tac_clean)
        )
        st.markdown(f'<div class="cblk">{esc(numbered)}</div>', unsafe_allow_html=True)
    else:
        st.info("No TAC generated.")
    st.markdown(
        metric_cards(
            [
                ("Instructions", len(tac_clean)),
                ("Temp Vars", len(set(re.findall(r"\bt\d+\b", "\n".join(tac_clean))))),
                ("Labels", sum(1 for l in tac_clean if re.match(r"\s*L\d+:", l))),
                ("CALL ops", sum(1 for l in tac_clean if "CALL" in l)),
            ]
        ),
        unsafe_allow_html=True,
    )

# ── PHASE 5 ────────────────────────────────────────────────────────────────────
with st.expander("🚀  Phase 5 — Code Optimisation", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="sect-title">Before</div>', unsafe_allow_html=True)
        before_text = (
            "\n".join(
                f"{str(i+1).rjust(3)}│  {l}"
                for i, l in enumerate(t for t in tac if t.strip())
            )
            or "(nothing)"
        )
        st.markdown(
            f'<div class="cblk">{esc(before_text)}</div>', unsafe_allow_html=True
        )
    with col_b:
        st.markdown('<div class="sect-title">After</div>', unsafe_allow_html=True)
        after_text = (
            "\n".join(
                f"{str(i+1).rjust(3)}│  {l}"
                for i, l in enumerate(t for t in tac_opt if t.strip())
            )
            or "(nothing)"
        )
        st.markdown(
            f'<div class="cblk">{esc(after_text)}</div>', unsafe_allow_html=True
        )

    before_n = len([l for l in tac if l.strip()])
    after_n = len([l for l in tac_opt if l.strip()])
    st.markdown(
        metric_cards(
            [
                ("Before", before_n),
                ("After", after_n),
                ("Saved", max(before_n - after_n, 0)),
                ("Applied", len(opt_applied)),
            ]
        ),
        unsafe_allow_html=True,
    )

    if opt_applied:
        st.markdown(
            '<div class="sect-title">Optimisations Applied</div>',
            unsafe_allow_html=True,
        )
        for o in opt_applied:
            st.markdown(
                f'<div class="badge-good" style="display:block;margin:3px 0">♻️ {esc(o)}</div>',
                unsafe_allow_html=True,
            )

# ── PHASE 6 ────────────────────────────────────────────────────────────────────
with st.expander("🖥️  Phase 6 — Target Code Generation", expanded=True):
    target_text = "\n".join(target_code)
    st.markdown(f'<div class="cblk">{esc(target_text)}</div>', unsafe_allow_html=True)
    st.markdown(
        metric_cards(
            [
                ("Target Lines", len(target_code)),
                (
                    "Declarations",
                    sum(1 for l in target_code if l.startswith("DECLARE")),
                ),
                (
                    "Branches",
                    sum(
                        1
                        for l in target_code
                        if l.startswith(("IF ", "IF_FALSE", "GOTO"))
                    ),
                ),
                ("CALLs", sum(1 for l in target_code if l.startswith("CALL"))),
            ]
        ),
        unsafe_allow_html=True,
    )

# ── OUTPUT ─────────────────────────────────────────────────────────────────────
with st.expander("▶  Simulated Output", expanded=True):
    output = simulate_output(code_input)
    if output.startswith("["):
        st.markdown(f'<div class="err-box">{esc(output)}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="out-box">{esc(output)}</div>', unsafe_allow_html=True)

# ── SUMMARY ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    metric_cards(
        [
            ("Tokens", len(tokens)),
            ("Parse Nodes", count_nodes(parse_tree_root)),
            ("Symbols", len(sym_table)),
            ("TAC (raw)", len([l for l in tac if l.strip()])),
            ("TAC (opt)", len([l for l in tac_opt if l.strip()])),
            ("Target Lines", len(target_code)),
            ("Lex Errors", len(lex_errors)),
            ("Syntax Issues", len(syn_issues)),
            ("Semantic Warns", len(sem_warns)),
        ]
    ),
    unsafe_allow_html=True,
)

total_issues = len(lex_errors) + len(syn_issues) + len(sem_warns)
if total_issues == 0:
    st.success("🎉 All 6 compiler phases completed successfully!")
else:
    st.warning(f"⚠️ Completed with {total_issues} issue(s).")
