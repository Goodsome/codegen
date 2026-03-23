# Resolve forward references for circular dependencies between AssignmentSpec and CallSpec
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.value_objects.call_spec import CallSpec

AssignmentSpec.model_rebuild()
CallSpec.model_rebuild()
