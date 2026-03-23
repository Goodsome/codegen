from typing import TYPE_CHECKING

from pydantic import Field

from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.config_spec import ConfigSpec
from codegen.domain_definition.domain.value_objects.container_spec import ContainerSpec

if TYPE_CHECKING:
    from codegen.domain_definition.domain.value_objects.bounded_context import BoundedContext
    from codegen.python_gen.domain.value_objects.package_spec import PackageSpec


class BootstrapSpec(ValueObject):
    """Specification of the bootstrap configuration."""

    config: ConfigSpec | None = Field(default=None)
    container: ContainerSpec | None = Field(default=None)

    def to_package_spec(
        self, contexts: list["BoundedContext"]
    ) -> "PackageSpec | None":
        """将 BootstrapSpec 转换为 PackageSpec

        Args:
            contexts: All bounded contexts with their configs

        Returns:
            PackageSpec for bootstrap package, or None if no bootstrap spec
        """
        from codegen.python_gen.domain.value_objects.package_spec import PackageSpec

        modules = []

        if self.config:
            config_module = self.config.to_app_config_module(contexts)
            modules.append(config_module)

        if self.container:
            container_module = self.container.to_app_container_module()
            modules.append(container_module)

        if not modules:
            return None

        return PackageSpec.create(name="bootstrap", modules=modules)
