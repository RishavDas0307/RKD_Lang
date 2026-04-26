# RKD_Lang

A dynamically-typed, interpreted programming language built from scratch in Python. RKD_Lang is a fully working language with a hand-written lexer, recursive descent parser, AST evaluator, closures, recursion, and a built-in standard library — no third-party dependencies.

---

## Features

- **Variables** — `let` bindings with re-assignment
- **Types** — integers, floats, strings, booleans, arrays, null
- **Arithmetic & comparison** — `+`, `-`, `*`, `/`, `%`, `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical operators** — `&&`, `||`, `!` with short-circuit evaluation
- **Control flow** — `if / else`, `while`, `for … in`
- **Functions** — first-class, anonymous (`fn` keyword), recursive
- **Closures** — functions capture their defining environment
- **Arrays** — literals, indexing, `push`, `pop`
- **String concatenation** — `+` operator across mixed types
- **Built-in stdlib** — `len`, `range`, `push`, `pop`, `int`, `float`, `str`, `sqrt`, `abs`, `max`, `min`, `input`
- **Comments** — `#` single-line
- **REPL** — interactive prompt with `:env` and `:help` commands

---

## Requirements

- Python 3.10+ (uses `match/case` pattern matching)
- No external dependencies

---

## Installation

```bash
git clone https://github.com/yourname/RKD_Lang.git
cd RKD_Lang
```

That's it.

---

## Usage

### REPL
```bash
python -m rkd
```
```
╔══════════════════════════════════════╗
║   RKD_Lang  v0.1   — type 'exit'    ║
╚══════════════════════════════════════╝
rkd> let x = 10
rkd> print(x * 2)
20
rkd> :env
  x = 10
rkd> exit
```

### Run a file
```bash
python -m rkd yourfile.rkd
```

---

## Language Tour

### Variables
```
let name = "Rishav"
let age  = 21
let pi   = 3.14
```

### Arithmetic & strings
```
let sum = 10 + 5 * 2      # 20  (precedence respected)
let msg = "Hello, " + name
```

### Conditionals
```
if age >= 18 {
    print("adult")
} else {
    print("minor")
}
```

### Loops
```
let i = 0
while i < 5 {
    print(i)
    i = i + 1
}

for item in [10, 20, 30] {
    print(item)
}
```

### Functions & recursion
```
let fib = fn(n) {
    if n <= 1 { return n }
    return fib(n - 1) + fib(n - 2)
}
print(fib(10))    # 55
```

### Closures
```
let make_counter = fn() {
    let count = 0
    return fn() {
        count = count + 1
        return count
    }
}
let counter = make_counter()
print(counter())    # 1
print(counter())    # 2
print(counter())    # 3
```

### Arrays
```
let nums = [1, 2, 3]
push(nums, 4)
print(nums[0])       # 1
print(len(nums))     # 4

for n in range(1, 6) {
    print(n)
}
```

---

## Project Structure

```
RKD_Lang/
├── rkd/
│   ├── tokens.py       Token types and Token dataclass
│   ├── lexer.py        Source text → token list
│   ├── ast_nodes.py    AST node definitions
│   ├── parser.py       Token list → AST (recursive descent)
│   ├── evaluator.py    AST → values (tree-walk interpreter)
│   └── __main__.py     REPL and file runner
└── demo.rkd            Example program
```

The pipeline is strictly linear:

```
source text  →  Lexer  →  tokens  →  Parser  →  AST  →  Evaluator  →  value
```

---

## Built-in Functions

| Function | Description |
|---|---|
| `print(x)` | Print a value to stdout |
| `len(x)` | Length of array or string |
| `range(start, stop)` | Array of integers from start to stop |
| `push(arr, val)` | Append val to array, returns array |
| `pop(arr)` | Remove and return last element |
| `int(x)` | Convert to integer |
| `float(x)` | Convert to float |
| `str(x)` | Convert to string |
| `input(prompt)` | Read a line from stdin |
| `sqrt(x)` | Square root |
| `abs(x)` | Absolute value |
| `max(a, b)` / `max(arr)` | Maximum value |
| `min(a, b)` / `min(arr)` | Minimum value |

---

## Roadmap

- [ ] Hashmaps `{"key": value}`
- [ ] String methods (`split`, `trim`, `upper`, `lower`)
- [ ] Better error messages with source line highlighting
- [ ] TypeScript port
- [ ] Browser-based playground (Monaco editor + live output)

---

## License

MIT
