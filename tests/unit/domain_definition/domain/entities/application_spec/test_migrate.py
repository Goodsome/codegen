from tests.unit.domain_definition.domain.entities.application_spec.bindings_migrate import (
    MigrateBindings,
    migrate_bindings,
)

_ = migrate_bindings


def test_migrate_collects_dtos_when_empty(migrate_bindings: MigrateBindings) -> None:
    migrate_bindings.given(
        "an ApplicationSpec where dtos is empty but use_cases have inputs/outputs"
    ).arrange_done().when("migrate() is called").then(
        "dtos is populated with all DtoSpecs collected from use_cases"
    )


def test_migrate_preserves_existing_dtos(migrate_bindings: MigrateBindings) -> None:
    migrate_bindings.given(
        "an ApplicationSpec where dtos already contains manually set DtoSpecs"
    ).arrange_done().when("migrate() is called").then("dtos remains unchanged")
