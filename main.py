import json
import os

from parser import TreeInfo
from utils import generate_module_path, get_allowed_doctypes, get_doctype_name


class PressAPIDocGenerator:
    BLACKLISTED_PATHS = [
        "backbone",
        "dashboard",
        "debugging",
        "deployment",
        "press/playbooks",
        "press/marketplace",
        "press/experimental",
        "press/press/report",
        "press/experimental",
        "press/www",
        "press/patches",
        "press/api/tests",
        "press/config",
        "press/scripts",
        "press/templates",
        "press/tests",
        "press/api/developer",
        "press/partner",
        "setup.py",
        "press/commands.py",
        "press/overrides.py",
        "press/agent.py",
        "press/exceptions.py",
        "press/hooks.py",
        "press/install.py",
        "press/auth.py",
        "press/telegram_utils.py",
        "press/__init__.py",
        "press/sanity.py",
        "press/bootstrap.py",
        "press/notifications.py",
        "press/metrics.py",
        "press/runner.py",
        "press/press/audit.py",
        "press/press/__init__.py",
        "press/press/cleanup.py",
    ]

    def __init__(self, target_path: str):
        # append target path to the blacklisted paths
        self.BLACKLISTED_PATHS = [
            os.path.join(target_path, path) for path in self.BLACKLISTED_PATHS
        ]
        self.allowed_doctypes = get_allowed_doctypes(target_path)
        self.parsed_objects: list[TreeInfo] = []
        # self.recurse(target_path, "")
        self.recurse("press/press", "press")

    def is_blacklisted(self, path):
        for blacklisted_path in self.BLACKLISTED_PATHS:
            if path.startswith(blacklisted_path):
                return True
        return False

    def recurse(self, path: str, base_module_path: str):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if (
                    file.endswith(".py")
                    and not self.is_blacklisted(file_path)
                    and not file.startswith("test_")
                ):
                    self.parsed_objects.append(
                        TreeInfo(
                            open(file_path).read(),
                            generate_module_path(base_module_path, file),
                        )
                    )
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                if not self.is_blacklisted(dir_path):
                    self.recurse(dir_path, generate_module_path(base_module_path, dir))

    def as_dict(self):
        return [obj.as_dict() for obj in self.parsed_objects]

    def generate_api_doc(self) -> dict:
        apis = {}  # group name -> [api]

        # frappe.whitelist methods
        for tree in self.parsed_objects:
            apis[tree.module_path] = []
            for fun in tree.functions:
                if fun.is_whitelisted_api:
                    apis[tree.module_path].append(
                        {
                            "method": "POST",
                            "path": f"/api/method/{tree.module_path}.{fun.name}",
                            "description": fun.docs,
                            "parameters": {
                                x.name: {
                                    "default": x.default,
                                    "type": x.annotation or "any",
                                }
                                for x in fun.args
                            },
                        }
                    )

        # add doctype specific methods - [run_doc_method, get, get_list]
        for tree in self.parsed_objects:
            for cls in tree.classes:
                doctype = get_doctype_name(cls.name)
                if doctype not in self.allowed_doctypes:
                    continue
                apis[cls.name] = []
                # press.api.client.run_doc_method
                for fun in cls.functions:
                    if not fun.is_whitelisted_method:
                        continue
                    data = {
                        "method": "POST",
                        "path": f"/api/method/press.api.client.run_doc_method",
                        "description": fun.docs,
                        "parameters": {
                            "dt": {
                                "default": doctype,
                                "type": "string",
                            },
                            "dn": {
                                "default": "Replace with the document name",
                                "type": "string",
                            },
                            "method": {
                                "default": fun.name,
                                "type": "string",
                            },
                        },
                    }
                    if fun.args:
                        data["parameters"]["args"] = {
                            x.name: {
                                "default": x.default,
                                "type": x.annotation or "any",
                            }
                            for x in fun.args
                        }
                    apis[cls.name].append(data)
                # press.api.client.get
                get_fields_documentation = f"""These fields will be available in the response:
- {', '.join(cls.dashboard_fields)}

Please note that, you can receive some additional fields as well. Try out the API to know more."""
                apis[cls.name].append(
                    {
                        "method": "POST",
                        "path": f"/api/method/press.api.client.get",
                        "description": get_fields_documentation,
                        "parameters": {
                            "doctype": {"default": doctype, "type": "str"},
                            "name": {
                                "default": "Replace with the document name",
                                "type": "str",
                            },
                        },
                    }
                )
                # press.api.client.get_list
                get_list_documentation = f"""These fields will be available in the response:
- {', '.join(cls.dashboard_fields)}

You can specify the required fields in `fields` parameter."""
                apis[cls.name].append(
                    {
                        "method": "POST",
                        "path": f"/api/method/press.api.client.get_list",
                        "description": get_list_documentation,
                        "parameters": {
                            "doctype": {"default": doctype, "type": "str"},
                            "fields": {
                                "default": str(cls.dashboard_fields),
                                "type": "list[str] | None",
                            },
                            "filters": {
                                "default": "Replace with the filters",
                                "type": "dict | None",
                            },
                            "order_by": {
                                "default": "Replace with the order_by",
                                "type": "str | None",
                            },
                            "start": {
                                "default": "0",
                                "type": "int",
                            },
                            "limit": {
                                "default": "100",
                                "type": "int",
                            },
                            "parent": {
                                "default": "Parent document name",
                                "type": "str | None",
                            },
                        },
                    }
                )
        # cleanup - remove records with no methods
        apis = {k: v for k, v in apis.items() if len(v) > 0}
        return apis


# print(json.dumps(PressAPIDocGenerator("press").as_dict(), indent=4))

api_specs = PressAPIDocGenerator("press").generate_api_doc()

with open("specs.json", "w") as f:
    json.dump(api_specs, f, indent=4)

# import ast

# x = """
# class Test:
#     def hemlock(self, a, b):
#         pass
        
# def hemlock(a, b):
#     pass

# """

# for node in ast.parse(x).body:
#     print(ast.dump(node))

# print(ast.dump(ast.parse(x)))
