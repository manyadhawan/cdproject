import compiler_visualizer as cv

source_code = """#include <stdio.h>
int main()
{
if(input==password){
        if(time<21){
            printf("Access Granted\\n");
        } else {
            printf("Late Night - Access Limited\\n");
        }
    } else {
        printf("Wrong Password\\n");
    }
return 0;
}"""

tokens, errors = cv.lex(source_code)
print("LEX ERRORS:", errors)

parser = cv.Parser(tokens)
ast = parser.parse()
print("PARSE ERRORS:", parser.errors)

sym_table, warnings = cv.semantic_analysis(tokens)
print("SEMANTIC WARNINGS:", warnings)
print("\nSYMBOL TABLE:")
for key, info in sym_table.items():
    print(f"  {key}: {info}")

tac = cv.generate_tac(ast)
for line in tac:
    print(line)
