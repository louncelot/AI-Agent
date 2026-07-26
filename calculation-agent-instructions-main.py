import argparse
import ast
import os
import re
from typing import Optional


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate arithmetic expressions in a text file")
    parser.add_argument("file_path", nargs="?", default="input.txt", help="Path to the input text file")
    return parser.parse_args()


def evaluate_expression(expression: str) -> Optional[float | int]:
    expr = expression.strip()
    if not expr:
        return None

    if re.search(r"[A-Za-z_]", expr):
        return None

    if not re.fullmatch(r"[0-9+\-*/().\s]+", expr):
        return None

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        return None

    def visit(node: ast.AST):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            operand = visit(node.operand)
            return operand if isinstance(node.op, ast.UAdd) else -operand

        if isinstance(node, ast.BinOp):
            left = visit(node.left)
            right = visit(node.right)

            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                if right == 0:
                    raise ZeroDivisionError("division by zero")
                return left / right

        raise ValueError("unsupported expression")

    try:
        result = visit(tree.body)
    except (ValueError, ZeroDivisionError, TypeError):
        return None

    if isinstance(result, float) and result.is_integer():
        return int(result)
    return result


def format_result(value: object) -> str:
    if value is None:
        return "ERROR"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def process_file(file_path: str) -> None:
    abs_path = os.path.abspath(file_path)

    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {abs_path}")

    with open(abs_path, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    processed = 0
    successful = 0
    failed = 0
    updated_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            updated_lines.append(line)
            continue

        if "=" in stripped and not re.fullmatch(r"[0-9+\-*/().\s]+", stripped.split("=", 1)[0].strip()):
            updated_lines.append(line)
            continue

        if re.fullmatch(r"[0-9+\-*/().\s]+", stripped):
            processed += 1
            result = evaluate_expression(stripped)

            if result is None:
                updated_lines.append(f"{stripped} = ERROR\n")
                failed += 1
            else:
                updated_lines.append(f"{stripped} = {format_result(result)}\n")
                successful += 1
        else:
            updated_lines.append(line)

    with open(abs_path, "w", encoding="utf-8") as handle:
        handle.writelines(updated_lines)

    print("Processing Complete")
    print("File Updated Successfully")
    print(f"Total Expressions Processed: {processed}")
    print(f"Successful Calculations: {successful}")
    print(f"Failed Calculations: {failed}")
    print(f"File Path: {abs_path}")


def main() -> None:
    args = parse_arguments()
    process_file(args.file_path)


if __name__ == "__main__":
    main()