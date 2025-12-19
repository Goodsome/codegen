
from codegen.domain.aggregates.blueprint import Blueprint

from codegen.domain.value_objects.layout_strategy import LayoutStrategy

from typing import List


class LayoutPlanner:
    """
    Plan output paths based on the selected layout strategy and blueprint.
    """
    
    def plan_paths(self, layout: LayoutStrategy, blueprint: Blueprint) -> List[str]:
        """
        Return a list of file paths that will be generated.
        """
        # TODO: Implement domain service logic
        pass
    