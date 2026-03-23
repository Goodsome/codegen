from typing import Any, Union

from pydantic import Field

from codegen.domain_definition.domain.value_objects.bootstrap_spec import BootstrapSpec
from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import ValueObject


class Blueprint(ValueObject):
    """Root of the generation model. Represents the entire project definition."""

    name: PascalString
    description: str
    layout: str = Field(default_factory=str)
    contexts: list[BoundedContext] = Field(default_factory=list)
    bootstrap: BootstrapSpec = Field(default_factory=BootstrapSpec)

    @classmethod
    def create(
        cls: Any,
        name: Union[str, PascalString],
        description: str,
        layout: str = "",
        contexts: list[BoundedContext] | None = None,
        bootstrap: BootstrapSpec | None = None,
    ) -> Any:

        if contexts is None:
            contexts = []
        if bootstrap is None:
            bootstrap = BootstrapSpec()
        if isinstance(name, str):
            name = PascalString(name)
        return cls(
            name=name,
            description=description,
            layout=layout,
            contexts=contexts,
            bootstrap=bootstrap,
        )

    def to_package_spec(self) -> "PackageSpec":
        """Convert this Blueprint to a PackageSpec."""
        from codegen.python_gen.domain.value_objects.package_spec import PackageSpec

        project_name = self.name.to_snake()
        context_packages = [
            c.to_package_spec(project_name=project_name) for c in self.contexts
        ]

        # Generate bootstrap package if blueprint has bootstrap spec
        if self.bootstrap:
            bootstrap_pkg = self.bootstrap.to_package_spec(self.contexts)
            if bootstrap_pkg:
                context_packages.append(bootstrap_pkg)

        return PackageSpec.create(
            name=project_name, sub_packages=context_packages
        )

    @classmethod
    def from_package_spec(cls, package_spec: "PackageSpec") -> "Blueprint":
        """Create a Blueprint from a PackageSpec."""
        from codegen.python_gen.domain.value_objects.package_spec import PackageSpec

        contexts = [
            BoundedContext.from_package_spec(p) for p in package_spec.sub_packages
        ]
        return cls.create(
            name=package_spec.name, description="", contexts=contexts, layout=""
        )
