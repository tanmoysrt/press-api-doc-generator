import ast
from utils import pretty_annotation, get_decorator_name


class FunctionArg:
    def __init__(self, arg: ast.arg):
        self.name = arg.arg
        self.annotation = pretty_annotation(arg.annotation)

    def __repr__(self):
        return f"FunctionArg(name={self.name}, annotation={self.annotation})"

    def as_dict(self):
        return {"type": "FunctionArg", "name": self.name, "annotation": self.annotation}


class FunctionInfo:
    def __init__(self, func: ast.FunctionDef):
        self.name = func.name
        if (
            len(func.body) > 0
            and hasattr(func.body[0], "value")
            and hasattr(func.body[0].value, "value")
            and isinstance(func.body[0].value.value, str)
        ):
            self.docs = func.body[0].value.value
        else:
            self.docs = ""
        self.args: list[FunctionArg] = []
        if hasattr(func, "args") and hasattr(func.args, "args"):
            for arg in func.args.args:
                if arg.arg == "self":
                    continue
                self.args.append(FunctionArg(arg))
        self.decorators: list[str] = []
        if hasattr(func, "decorator_list"):
            for decorator in func.decorator_list:
                decorator_name = get_decorator_name(decorator)
                if decorator_name:
                    self.decorators.append(decorator_name)

        self.is_whitelisted_api = "frappe.whitelist" in self.decorators
        self.is_whitelisted_method = "dashboard_whitelist" in self.decorators

    def __repr__(self):
        return f"FunctionInfo(name={self.name}, docs={self.docs}), args={self.args}, decorators={self.decorators}, is_whitelisted_api={self.is_whitelisted_api}, is_whitelisted_method={self.is_whitelisted_method}"

    def as_dict(self):
        return {
            "type": "Function",
            "name": self.name,
            "docs": self.docs,
            "args": [arg.as_dict() for arg in self.args],
            "decorators": self.decorators,
            "is_whitelisted_api": self.is_whitelisted_api,
            "is_whitelisted_method": self.is_whitelisted_method,
        }


class ClassInfo:
    def __init__(self, cls: ast.ClassDef):
        self.name = cls.name
        self.functions: list[FunctionInfo] = []
        self.dashboard_fields: list[str] = []
        if hasattr(cls, "body"):
            for node in cls.body:
                if isinstance(node, ast.FunctionDef):
                    self.functions.append(FunctionInfo(node))
                if isinstance(node, ast.Assign):
                    if (
                        node.targets
                        and node.targets[0].id == "dashboard_fields"
                        and hasattr(node.value, "elts")
                        and isinstance(node.value.elts, list)
                    ):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant):
                                self.dashboard_fields.append(elt.value)

    def __repr__(self):
        return f"ClassInfo(name={self.name}, dashboard_fields={self.dashboard_fields}, functions={self.functions})"

    def as_dict(self):
        return {
            "type": "Class",
            "name": self.name,
            "dashboard_fields": self.dashboard_fields,
            "functions": [func.as_dict() for func in self.functions],
        }


class TreeInfo:
    def __init__(self, content: str, module_path: str):
        self.classes: list[ClassInfo] = []
        self.functions: list[FunctionInfo] = []
        self.module_path: str = module_path

        for node in ast.walk(ast.parse(content)):
            if isinstance(node, ast.ClassDef):
                self.classes.append(ClassInfo(node))
            elif isinstance(node, ast.FunctionDef):
                self.functions.append(FunctionInfo(node))

    def __repr__(self):
        return f"TreeInfo(module_path={self.module_path}, classes={self.classes}, functions={self.functions})"

    def as_dict(self):
        return {
            "type": "Tree",
            "module_path": self.module_path,
            "classes": [cls.as_dict() for cls in self.classes],
            "functions": [func.as_dict() for func in self.functions],
        }
