from dataclasses import dataclass
from typing import Self

import pytest

from codegen.domain_definition.domain.entities.application_spec import ApplicationSpec
from codegen.domain_definition.domain.entities.dto_spec import DtoSpec
from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString


@dataclass
class MigrateBindings:
    _last_step_type: str | None = None
    _app: ApplicationSpec | None = None
    _dtos_before: list[DtoSpec] | None = None

    def given(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "given"
        match semantic_text:
            case "an ApplicationSpec where dtos is empty but use_cases have inputs/outputs":
                uc_create_order = UseCaseSpec.create(
                    name="CreateOrder",
                    kind=UseCaseKind.COMMAND,
                    inputs=[
                        AttributeSpec.create(name="user_id", type="str"),
                        AttributeSpec.create(name="amount", type="float"),
                    ],
                    outputs=[
                        AttributeSpec.create(name="order_id", type="str"),
                    ],
                )
                uc_get_order = UseCaseSpec.create(
                    name="GetOrder",
                    kind=UseCaseKind.QUERY,
                    inputs=[
                        AttributeSpec.create(name="order_id", type="str"),
                    ],
                    outputs=[
                        AttributeSpec.create(name="order_data", type="dict"),
                    ],
                )
                self._app = ApplicationSpec(
                    use_cases=[uc_create_order, uc_get_order],
                )
            case "an ApplicationSpec where dtos already contains manually set DtoSpecs":
                manual_dto = DtoSpec(
                    name=PascalString("ManualDto"),
                    description="manually set",
                    base_types=["BaseModel"],
                )
                self._app = ApplicationSpec(dtos=[manual_dto])
            case _:
                raise NotImplementedError(f"未实现的 given 语义: {semantic_text}")
        return self

    def arrange_done(self: Self) -> Self:
        return self

    def when(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "when"
        match semantic_text:
            case "migrate() is called":
                assert self._app is not None, "ApplicationSpec must be set in given step"
                self._dtos_before = list(self._app.dtos)
                self._app.migrate()
            case _:
                raise NotImplementedError(f"未实现的 when 语义: {semantic_text}")
        return self

    def then(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "then"
        match semantic_text:
            case "dtos is populated with all DtoSpecs collected from use_cases":
                assert self._app is not None
                assert len(self._app.dtos) == 4
                dto_names = {str(d.name) for d in self._app.dtos}
                assert dto_names == {
                    "CreateOrderCommand",
                    "CreateOrderResult",
                    "GetOrderQuery",
                    "GetOrderResult",
                }
            case "dtos remains unchanged":
                assert self._app is not None
                assert self._dtos_before is not None
                assert self._app.dtos == self._dtos_before
                assert len(self._app.dtos) == 1
                assert str(self._app.dtos[0].name) == "ManualDto"
            case _:
                raise NotImplementedError(f"未实现的 then 语义: {semantic_text}")
        return self

    def and_(self: Self, semantic_text: str) -> Self:
        if not self._last_step_type:
            raise RuntimeError("Cannot use 'and/but' before any Given/When/Then step.")
        if self._last_step_type == "given":
            return self.given(semantic_text)
        if self._last_step_type == "when":
            return self.when(semantic_text)
        if self._last_step_type == "then":
            return self.then(semantic_text)
        raise RuntimeError(f"Unexpected last step type: {self._last_step_type}")

    def but(self: Self, semantic_text: str) -> Self:
        if not self._last_step_type:
            raise RuntimeError("Cannot use 'and/but' before any Given/When/Then step.")
        if self._last_step_type == "given":
            return self.given(semantic_text)
        if self._last_step_type == "when":
            return self.when(semantic_text)
        if self._last_step_type == "then":
            return self.then(semantic_text)
        raise RuntimeError(f"Unexpected last step type: {self._last_step_type}")


@pytest.fixture
def migrate_bindings() -> MigrateBindings:
    return MigrateBindings()
