Compiler Phase Visualizer

A Streamlit-based Compiler Simulator that demonstrates all six phases of a compiler by converting C code into tokens, syntax trees, intermediate code, optimized code, and final assembly output.

🚀 Overview

This project simulates how a compiler works internally by breaking down the process into six distinct phases:

Lexical Analysis
Syntax Analysis
Semantic Analysis
Intermediate Code Generation
Code Optimization
Code Generation

It also includes output simulation, making it easy to understand the complete compilation pipeline.

✨ Features
🔤 Token generation using lexical analysis
🌳 Parse Tree and AST visualization
📊 Symbol Table construction and validation
⚡ Three Address Code (TAC) generation
🚀 Code optimization techniques
🖥️ Assembly-like code generation
▶️ Output simulation
🎨 Interactive UI using Streamlit
🧠 Compiler Phases Explained
🔤 Phase 1: Lexical Analysis
Converts source code into tokens
Identifies keywords, identifiers, operators, and constants
Removes comments and whitespace
🌳 Phase 2: Syntax Analysis
Validates grammar of the code
Generates:
Parse Tree (detailed structure)
Abstract Syntax Tree (AST)
🔍 Phase 3: Semantic Analysis
Builds a Symbol Table
Checks:
Variable declarations
Scope
Type consistency
Errors like undeclared variables
⚡ Phase 4: Intermediate Code Generation
Converts code into Three Address Code (TAC)
Uses temporary variables (t1, t2, etc.)

Example:

a = b + c

⬇️

t1 = b + c
a = t1
🚀 Phase 5: Code Optimization

Applies optimization techniques such as:

Constant Folding
Constant Propagation
Dead Code Elimination
🖥️ Phase 6: Code Generation
Converts optimized TAC into assembly-like instructions
Uses registers like EAX, EBX

Example:

MOV EAX, 5
MOV [a], EAX
▶️ Output Simulation
