from tests.unit.domain_definition.domain.entities.application_spec.bindings_package_spec import (
    PackageSpecRoundtripBindings,
    package_spec_roundtrip_bindings,
)

_ = package_spec_roundtrip_bindings


def test_package_spec_roundtrip_preserves_dtos(
    package_spec_roundtrip_bindings: PackageSpecRoundtripBindings,
) -> None:
    package_spec_roundtrip_bindings.given(
        "an ApplicationSpec containing dtos"
    ).arrange_done().when(
        "to_package_spec() is called"
    ).then(
        "the PackageSpec contains a dtos sub-package"
    ).when(
        "from_package_spec() is called on the resulting PackageSpec"
    ).then(
        "the restored ApplicationSpec has the same dtos"
    )
