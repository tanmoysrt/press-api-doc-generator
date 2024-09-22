import ast
import contextlib


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
        return str(annotation)


def generate_module_path(base_module_path: str, file_or_dir: str):
    if file_or_dir == "__init__.py":
        return base_module_path
    file_or_dir = file_or_dir.split(".")[0]
    if base_module_path:
        return base_module_path + "." + file_or_dir
    return file_or_dir
