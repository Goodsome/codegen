from typing import Self, Union

from pydantic import Field

from codegen.code_metadata.application.dtos.upsert_component_command import UpsertComponentCommand
from codegen.domain_definition.domain.entities.bootstrap_spec import BootstrapSpec
from codegen.domain_definition.domain.entities.bounded_context import BoundedContext
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.core.aggregate_root import AggregateRoot
from codegen.shared.domain.value_objects.pascal_string import PascalString


class Blueprint(AggregateRoot[str]):
    """Root of the generation model. Represents the entire project definition."""

    name: PascalString
    contexts: list[BoundedContext] = Field(default_factory=list)
    bootstrap: BootstrapSpec = Field(default_factory=BootstrapSpec)

    @classmethod
    def create(
        cls: type[Self],
        name: Union[str, PascalString],
        contexts: list[BoundedContext] | None = None,
        bootstrap: BootstrapSpec | None = None,
    ) -> Self:
        if contexts is None:
            contexts = []
        if bootstrap is None:
            bootstrap = BootstrapSpec()
        if isinstance(name, str):
            name = PascalString(name)
        return cls(
            id="codegen",
            name=name,
            contexts=contexts,
            bootstrap=bootstrap,
        )

    def to_package_spec(self: Self) -> PackageSpec:
        """Convert this Blueprint to a PackageSpec."""
        project_name = self.name.to_snake()
        context_packages = [
            c.to_package_spec() for c in self.contexts
        ]
        if self.bootstrap:
            bootstrap_pkg = self.bootstrap.to_package_spec(self.contexts)
            if bootstrap_pkg:
                context_packages.append(bootstrap_pkg)
        p = PackageSpec.create(name=project_name, sub_packages=context_packages)
        return PackageSpec.create(name="src", sub_packages=[p])

    @classmethod
    def from_package_spec(cls: type[Self], package_spec: PackageSpec) -> Self:
        """Create a Blueprint from a PackageSpec."""
        contexts = [
            BoundedContext.from_package_spec(p)
            for p in package_spec.sub_packages
            if p.name != "entrypoints"
        ]
        return cls.create(
            name=package_spec.name,
            contexts=contexts,
        )

    def remove_context(self: Self, name: str) -> Self:
        """Remove a BoundedContext by name. Returns self for chaining."""
        self.contexts = [ctx for ctx in self.contexts if ctx.name != name]
        return self

    def get_context(self: Self, name: str) -> BoundedContext:
        """Get a BoundedContext by name. Raises ValueError if not found."""
        for ctx in self.contexts:
            if ctx.name == PascalString(name):
                return ctx
        raise ValueError(f"Context '{name}' not found in blueprint")

    def to_test_package_spec(self: Self) -> PackageSpec:
        """Create top-level tests package with unit subpackage containing all context tests."""
        context_packages = [ctx.to_test_package_spec() for ctx in self.contexts]
        unit_pkg = PackageSpec.create(name="unit", sub_packages=context_packages)
        integration_pkg = PackageSpec.create(
            name="integration",
            sub_packages=[
                ctx.to_integration_test_package_spec() for ctx in self.contexts
            ],
        )
        return PackageSpec.create(
            name="tests", sub_packages=[unit_pkg, integration_pkg]
        )

    def load_test_package(self: Self, test_pkg: PackageSpec) -> Self:
        """Load test package into the blueprint. Returns self for chaining."""
        if test_pkg.name != "tests":
            return self
        for pkg in test_pkg.sub_packages:
            for ctx_pkg in pkg.sub_packages:
                ctx = self.get_context(ctx_pkg.name)
                ctx.load_test_package(ctx_pkg)
        return self

    def collect_components(self: Self) -> list[UpsertComponentCommand]:
        """Collect all components from the blueprint."""
        components: list[UpsertComponentCommand] = []
        for ctx in self.contexts:
            components.extend(ctx.collect_components())
        return components