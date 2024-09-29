import json
import os

from parser import TreeInfo
from utils import generate_module_path


class PressAPIGenerator:
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
        "press/saas",
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
        "press/press/doctype",
    ]

    def __init__(self, target_path: str):
        # append target path to the blacklisted paths
        self.BLACKLISTED_PATHS = [
            os.path.join(target_path, path) for path in self.BLACKLISTED_PATHS
        ]
        self.parsed_objects: list[TreeInfo] = []
        # self.recurse(target_path, "")
        self.recurse("press/press/api", "press.api")

    def is_blacklisted(self, path):
        for blacklisted_path in self.BLACKLISTED_PATHS:
            if path.startswith(blacklisted_path):
                return True
        return False

    def recurse(self, path: str, base_module_path: str):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".py") and not self.is_blacklisted(file_path):
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
        paths = {}
        tags = []
        for tree in self.parsed_objects:
            for fun in tree.functions:
                if fun.is_whitelisted_api:
                    paths[f"/api/method/{tree.module_path}.{fun.name}"] = {
                        "post": {
                            "tags": [tree.module_path],
                            "description": fun.docs,
                            "requestBody": {
                                "required": len(fun.args) > 0,
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                x.name: {
                                                    "type": x.annotation,
                                                }
                                                for x in fun.args
                                            },
                                            "required": [x.name for x in fun.args],
                                        }
                                    }
                                },
                            },
                            "responses": {"200": {"description": "Successful"}},
                        }
                    }

            if len(tree.functions) > 0:
                tags.append(
                    {
                        "name": tree.module_path,
                    }
                )

        # sort tags by name
        tags.sort(key=lambda x: x["name"])

        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Frappe Cloud API",
                "description": "API documentation for Frappe Cloud",
                "version": "1.0.0",
            },
            "servers": [
                {
                    "url": "https://frappecloud.com/v1",
                    "description": "Production server",
                }
            ],
            "paths": paths,
            "tags": tags,
        }


# recurse("press/press/api", "press.api")

# print(len(parsed_objects))
# print(json.dumps([obj.as_dict() for obj in parsed_objects], indent=4))


# def parse_api_docs(file_path, module_path):
#     content = open(file_path).read()
#     print(TreeInfo(content, module_path).as_dict())


# parse_api_docs(
#     "press/press/press/doctype/site/site.py", "press.press.doctype.site.site"
# )


# print(json.dumps(PressAPIGenerator("press").as_dict(), indent=4))

api_specs = PressAPIGenerator("press").generate_api_doc()

with open("specs.json", "w") as f:
    json.dump(api_specs, f, indent=4)
