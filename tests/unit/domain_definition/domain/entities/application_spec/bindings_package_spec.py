from dataclasses import dataclass
from typing import Self

import pytest

from codegen.domain_definition.domain.entities.application_spec import ApplicationSpec
from codegen.domain_definition.domain.entities.dto_spec import DtoSpec
from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString


@dataclass
class PackageSpecRoundtripBindings:
    _last_step_type: str | None = None
    _app: ApplicationSpec | None = None
    _pkg: PackageSpec | None = None
    _restored: ApplicationSpec | None = None

    def given(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "given"
        match semantic_text:
            case "an ApplicationSpec containing dtos":
                uc = UseCaseSpec.create(
                    name="CreateOrder",
                    kind=UseCaseKind.COMMAND,
                    inputs=[
                        AttributeSpec.create(name="user_id", type="str"),
                    ],
                    outputs=[
                        AttributeSpec.create(name="order_id", type="str"),
                    ],
                )
                self._app = ApplicationSpec(
                    use_cases=[uc],
                    dtos=[
                        DtoSpec(
                            name=PascalString("CreateOrderCommand"),
                            description="",
                            base_types=["BaseModel"],
                        ),
                        DtoSpec(
                            name=PascalString("CreateOrderResult"),
                            description="",
                            base_types=["BaseModel"],
                        ),
                    ],
                )
            case _:
                raise NotImplementedError(f"未实现的 given 语义: {semantic_text}")
        return self

    def arrange_done(self: Self) -> Self:
        return self

    def when(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "when"
        match semantic_text:
            case "to_package_spec() is called":
                assert self._app is not None
                self._pkg = self._app.to_package_spec()
            case "from_package_spec() is called on the resulting PackageSpec":
                assert self._pkg is not None
                self._restored = ApplicationSpec.from_package_spec(self._pkg)
            case _:
                raise NotImplementedError(f"未实现的 when 语义: {semantic_text}")
        return self

    def then(self: Self, semantic_text: str) -> Self:
        self._last_step_type = "then"
        match semantic_text:
            case "the PackageSpec contains a dtos sub-package":
                assert self._pkg is not None
                dtos_sub = [
                    sp for sp in self._pkg.sub_packages if sp.name == "dtos"
                ]
                assert len(dtos_sub) == 1
                non_init_modules = [
                    m for m in dtos_sub[0].modules if not m.is_init_module()
                ]
                assert len(non_init_modules) == 2
            case "the restored ApplicationSpec has the same dtos":
                assert self._restored is not None
                assert self._app is not None
                assert len(self._restored.dtos) == len(self._app.dtos)
                restored_names = {str(d.name) for d in self._restored.dtos}
                original_names = {str(d.name) for d in self._app.dtos}
                assert restored_names == original_names
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
def package_spec_roundtrip_bindings() -> PackageSpecRoundtripBindings:
    return PackageSpecRoundtripBindings()
