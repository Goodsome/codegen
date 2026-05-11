from tests.unit.domain_definition.domain.entities.use_case_spec.bindings_collect_dtos import (
    CollectDtosBindings,
    collect_dtos_bindings,
)

_ = collect_dtos_bindings


def test_use_case_with_inputs_outputs_returns_two_dtos(
    collect_dtos_bindings: CollectDtosBindings,
) -> None:
    collect_dtos_bindings.given(
        "a UseCaseSpec (kind=COMMAND) with inputs and outputs"
    ).arrange_done().when("collect_dtos() is called").then(
        "return two DtoSpecs: one named {Name}Command (attributes from inputs), one named {Name}Result (attributes from outputs)"
    )


def test_use_case_without_inputs_outputs_returns_empty(
    collect_dtos_bindings: CollectDtosBindings,
) -> None:
    collect_dtos_bindings.given(
        "a UseCaseSpec with empty inputs and outputs"
    ).arrange_done().when("collect_dtos() is called").then("return an empty list")
