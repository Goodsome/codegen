from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec


class ModuleToParsedComponent:

    @classmethod
    def execute(cls, module: ModuleSpec) -> ParsedComponent:
        assert module.path is not None
        cls = module.get_class(module.name)
        return ParsedComponent(
            path=module.path,
            name=cls.name,
            description=cls.description,
        )
        