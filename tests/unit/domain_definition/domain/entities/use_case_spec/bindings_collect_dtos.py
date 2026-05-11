from dataclasses import dataclass, field
from typing import Self

import pytest

from codegen.domain_definition.domain.entities.dto_spec import DtoSpec
from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec


@dataclass
class CollectDtosBindings:
    _last_step_type: str | None = None
    _use_case: UseCaseSpec | None = None
    _result: list[DtoSpec] = field(default_factory=list)

    def given(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "given"
        match semantic_text:
            case "a UseCaseSpec (kind=COMMAND) with inputs and outputs":
                self._use_case = UseCaseSpec.create(
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
            case "a UseCaseSpec with empty inputs and outputs":
                self._use_case = UseCaseSpec.create(
                    name="NoOp",
                    kind=UseCaseKind.QUERY,
                )
            case _:
                raise NotImplementedError(f"未实现的 given 语义: {semantic_text}")
        return self

    def arrange_done(self: Self) -> Self:
        return self

    def when(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "when"
        match semantic_text:
            case "collect_dtos() is called":
                assert self._use_case is not None, "UseCaseSpec must be set in given step"
                self._result = self._use_case.collect_dtos()
            case _:
                raise NotImplementedError(f"未实现的 when 语义: {semantic_text}")
        return self

    def then(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "then"
        match semantic_text:
            case "return two DtoSpecs: one named {Name}Command (attributes from inputs), one named {Name}Result (attributes from outputs)":
                assert self._use_case is not None
                assert len(self._result) == 2

                input_dto = self._result[0]
                output_dto = self._result[1]

                assert str(input_dto.name) == "CreateOrderCommand"
                assert input_dto.base_types == ["BaseModel"]
                assert input_dto.description == ""
                input_attr_names = [str(a.name) for a in input_dto.attributes]
                assert "user_id" in input_attr_names
                assert "amount" in input_attr_names

                assert str(output_dto.name) == "CreateOrderResult"
                assert output_dto.base_types == ["BaseModel"]
                assert output_dto.description == ""
                output_attr_names = [str(a.name) for a in output_dto.attributes]
                assert "order_id" in output_attr_names
            case "return an empty list":
                assert self._result == []
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
def collect_dtos_bindings() -> CollectDtosBindings:
    return CollectDtosBindings()
