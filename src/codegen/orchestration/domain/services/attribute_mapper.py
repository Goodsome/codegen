from dataclasses import dataclass, field
from codegen.python_gen.domain.value_objects.variable_spec import (
    VariableSpec,
)
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.enums import FieldFlavor, AssignmentFlavor
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.orchestration.domain.services.type_system_converter import (
    TypeSystemConverter,
)


@dataclass
class AttributeMapper:
    type_system_converter: TypeSystemConverter = field(default_factory=TypeSystemConverter)

    def to_variable_spec(
        self,
        attribute: AttributeSpec,
        default_field_flavor: FieldFlavor | None = None,
    ) -> VariableSpec:
        annotation = self.type_system_converter.to_python_annotation(attribute)

        assignment = None
        if attribute.default is not None:
            # Explicit default value takes precedence
            assignment = AssignmentSpec.from_code(attribute.default)
            
            # If default_field_flavor is set and optional, wrap it?
            # If we have an explicit default, we generally trust it.
            # But if it is a Pydantic model, we might need Field(default=...).
            if default_field_flavor:
                 func_name = "Field" if default_field_flavor == FieldFlavor.PYDANTIC else "field"
                 assignment = AssignmentSpec.from_call(
                    func_name=func_name,
                    kwargs={"default": assignment}
                 )
        elif default_field_flavor and attribute.optional:
            # Create default=Field(default=None) or similar
            # Logic: If optional, default is usually None.
            # If using Pydantic Field, we want Field(default=None).
            # If using generic field, field(default=None).
            
            func_name = "Field" if default_field_flavor == FieldFlavor.PYDANTIC else "field"
            kwargs = {}
            if annotation.name == "None": # Logic check if it is explicitly None? 
                # Attribute optional=True means python type is Optional[T] or T | None.
                # So default value should be None.
                kwargs["default"] = AssignmentSpec.from_literal("None") # "None" string literal or None value?
                # AssignmentSpec from_literal(None) -> value=None.
                # But rendered? Constant(value=None).
            else:
                 kwargs["default"] = AssignmentSpec.from_literal(None)
            
            assignment = AssignmentSpec.from_call(
                func_name=func_name,
                kwargs=kwargs
            )
        elif attribute.optional:
            # Just default=None without Field wrapper?
            # Or if it's a parameter in function -> default=None.
            # If it's a class attribute without Field -> standard default.
            # AttributeMapper is used for both Dataclasses/Pydantic models (need Field) and function args (no Field).
            # Use 'default_field_flavor' to decide.
            if default_field_flavor:
                func_name = "Field" if default_field_flavor == FieldFlavor.PYDANTIC else "field"
                assignment = AssignmentSpec.from_call(
                    func_name=func_name,
                    kwargs={"default": AssignmentSpec.from_literal(None)}
                )
            else:
                assignment = AssignmentSpec.from_literal(None)

        return VariableSpec.create(
            name=attribute.name,
            type_spec=annotation,
            assignment=assignment,
        )

    def to_attribute(self, variable_spec: VariableSpec) -> AttributeSpec:
        generic_type, container, is_optional, custom_type_string = (
            self.type_system_converter.from_python_annotation(variable_spec.type_spec)
        )
        
        default_value = None
        if variable_spec.assignment:
             if variable_spec.assignment.code:
                 default_value = variable_spec.assignment.code
             elif variable_spec.assignment.literal:
                 default_value = repr(variable_spec.assignment.literal.value)
        
        if variable_spec.assignment and variable_spec.assignment.flavor == AssignmentFlavor.CALL:
             call = variable_spec.assignment.call
             if call and call.callee in ("Field", "field"):
                 if "default" in call.kwargs:
                     default_arg = call.kwargs["default"]
                     if default_arg.code:
                         default_value = default_arg.code
                     elif default_arg.literal:
                         default_value = repr(default_arg.literal.value)

                     if default_arg.flavor == AssignmentFlavor.LITERAL and default_arg.literal.value is None:
                         is_optional = True
                         default_value = None
                 elif "default_factory" in call.kwargs:
                     is_optional = True
                     default_value = None

        # Check assignment to confirm optionality?
        # If type says optional, fine.
        # If assignment is 'None', it reinforces optional but type is source of truth?
        # Keep existing logic relying on type annotation.

        return AttributeSpec(
            name=variable_spec.name,
            type=generic_type,
            container=container,
            optional=is_optional,
            default=default_value,
            custom_type_string=custom_type_string,
        )

    def to_variable_specs(
        self,
        attributes: list[AttributeSpec],
        default_field_flavor: FieldFlavor | None = None,
    ) -> list[VariableSpec]:
        return [
            self.to_variable_spec(attr, default_field_flavor) for attr in attributes
        ]

    def to_attributes(
        self, variable_specs: list[VariableSpec]
    ) -> list[AttributeSpec]:
        return [self.to_attribute(spec) for spec in variable_specs]
