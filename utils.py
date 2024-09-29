import ast
import contextlib
import os


def get_decorator_name(decorator) -> str:
    with contextlib.suppress(Exception):
        if isinstance(decorator, ast.Call):
            func = decorator.func
            if hasattr(func, "attr"):
                return f"{func.value.id}.{func.attr}"
            elif hasattr(func, "id"):
                return func.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}"
    return ""


def pretty_annotation(annotation) -> str:
    # int, str, bool
    if isinstance(annotation, ast.Name):
        return annotation.id
    # list[str], dict[int, str]
    elif isinstance(annotation, ast.Subscript):
        base_type = pretty_annotation(annotation.value)
        subscript_type = pretty_annotation(annotation.slice)
        return f"{base_type}[{subscript_type}]"
    # dict[int, str]
    elif isinstance(annotation, ast.Tuple):
        return ", ".join(pretty_annotation(elt) for elt in annotation.elts)
    elif isinstance(annotation, ast.Attribute):
        return annotation.attr
    else:
        if annotation is None:
            return ""
        return ast.unparse(annotation)


def generate_module_path(base_module_path: str, file_or_dir: str):
    if file_or_dir == "__init__.py":
        return base_module_path
    file_or_dir = file_or_dir.split(".")[0]
    if base_module_path:
        return base_module_path + "." + file_or_dir
    return file_or_dir


def get_allowed_doctypes(base_path: str) -> list[str]:
    path = os.path.join(base_path, "press/api/client.py")
    with open(path) as f:
        content = f.read()
    parsed = ast.parse(content)
    # looks for ALLOWED_DOCTYPES
    for node in ast.walk(parsed):
        if isinstance(node, ast.Assign):
            if (
                node.targets
                and node.targets[0].id == "ALLOWED_DOCTYPES"
                and hasattr(node.value, "elts")
                and isinstance(node.value.elts, list)
            ):
                return [elt.value for elt in node.value.elts]
    return []


def get_doctype_name(text):
    result = []
    for i, char in enumerate(text):
        if i > 0:
            if char.isupper():
                if (i < len(text) - 1 and text[i + 1].islower()) or text[i - 1].islower():
                    result.append(" ")
        result.append(char)
    return "".join(result)
