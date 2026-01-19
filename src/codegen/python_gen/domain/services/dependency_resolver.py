from typing import Iterable
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from dataclasses import dataclass

from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec

import logging

logger = logging.getLogger(__name__)


BUILTIN_TYPES = {
    "str",
    "int",
    "float",
    "bool",
    "None",
    "list",
    "dict",
    "tuple",
    "staticmethod",
    "classmethod",
}

GLOBAL_REGISTRY = {
    "Field": "pydantic",
    "BaseModel": "pydantic",
    "Path": "pathlib",
    "Any": "typing",
    "Dict": "typing",
    "Union": "typing",
    "Iterable": "typing",
    "Iterator": "typing",
    "dataclass": "dataclasses",
    "field": "dataclasses",
    "ABC": "abc",
    "abstractmethod": "abc",
    "datetime": "datetime",
    "UUID": "uuid",
}

TEMPORARY_MAPPING = {"dataclass(frozen=True)": "dataclass"}


@dataclass
class DependencyResolver:

    global_registry: dict[str, str]

    @classmethod
    def build_from_package_spec(cls, package_spec: PackageSpec) -> "DependencyResolver":
        global_registry = package_spec.get_global_registry()
        global_registry.update(GLOBAL_REGISTRY)
        return cls(global_registry=global_registry)

    def resolve_module(self, module_spec: ModuleSpec) -> Iterable[ImportFromSpec]:
        required_types = module_spec.get_required_types()
        import_spec_bags: dict[str, ImportFromSpec] = {}
        for import_spec in module_spec.imports:
            import_spec_bags[import_spec.module] = import_spec
        for rt in required_types:
            if module_spec.has_class_or_function(rt):
                continue
            if rt in BUILTIN_TYPES:
                continue
            rt = TEMPORARY_MAPPING.get(rt, rt)
            if rt not in self.global_registry:
                logger.warning(f"Could not find type {rt} in global registry")
                continue
            module_path = self.global_registry[rt]
            if module_path not in import_spec_bags:
                import_spec_bags[module_path] = ImportFromSpec(
                    module=module_path, names=[]
                )
            import_spec_bags[module_path].add_name(rt)

        return import_spec_bags.values()
