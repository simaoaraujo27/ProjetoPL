from pathlib import Path

from EWVM.vm_codegen import VMCodeGenerator
from IR.ir_generator import IRGenerator
from Parser import parse_code
from Semantic import SemanticAnalyzer


def _resolve_existing_path(path_str):
    candidate = Path(path_str)
    if candidate.exists():
        return candidate

    parts = candidate.parts
    if not parts:
        return candidate

    current = Path(parts[0]) if candidate.is_absolute() else Path(".")
    start_index = 1 if candidate.is_absolute() else 0

    for part in parts[start_index:]:
        if not current.is_dir():
            return candidate

        match = None
        for child in current.iterdir():
            if child.name.lower() == part.lower():
                match = child
                break

        if match is None:
            return candidate
        current = match

    return current


def compile_to_vm(source_code):
    ast = parse_code(source_code)
    symbol_table = SemanticAnalyzer().analyze(ast)
    ir_program = IRGenerator(symbol_table).generate(ast)
    return VMCodeGenerator(symbol_table).generate(ir_program)


def compile_file(input_path, output_path=None):
    input_file = _resolve_existing_path(input_path)
    source_code = input_file.read_text(encoding="utf-8")
    vm_code = compile_to_vm(source_code)

    if output_path is None:
        output_file = input_file.with_suffix(".vm")
    else:
        output_file = Path(output_path)

    output_file.write_text(vm_code, encoding="utf-8")
    return output_file


def main(argv=None):
    import sys

    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        raise SystemExit("Uso: python3 compiler.py <ficheiro.f> [ficheiro.vm]")

    input_path = args[0]
    output_path = args[1] if len(args) > 1 else None
    output_file = compile_file(input_path, output_path)
    print(output_file)


if __name__ == "__main__":
    main()
