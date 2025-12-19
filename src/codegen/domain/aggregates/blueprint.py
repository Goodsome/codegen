from typing import List, Dict, Any
from codegen.domain.shared.models import AggregateRoot
from codegen.domain.value_objects.bounded_context import BoundedContext
from codegen.domain.value_objects.aggregate import Aggregate
from codegen.domain.value_objects.value_spec import ValueSpec
from codegen.domain.value_objects.service import Service
from codegen.domain.value_objects.port import Port
from codegen.domain.value_objects.use_case import UseCase
from codegen.domain.value_objects.operation import Operation
from codegen.domain.value_objects.attribute import Attribute
from codegen.domain.value_objects.command import Command
from codegen.domain.value_objects.result import Result

class Blueprint(AggregateRoot):
    """Root of the generation model. Represents the entire project definition."""

    name: str
    layout: str
    contexts: List[BoundedContext]

    def load_from_dict(self, data: Dict[str, Any]):
        self.name = data.get("name", "Unknown")
        self.layout = data.get("layout", "standard")
        self.contexts = []
        
        for ctx_data in data.get("contexts", []):
            domain = ctx_data.get("domain", {})
            app = ctx_data.get("application", {})
            
            aggregates = []
            for agg_data in domain.get("aggregates", []):
                aggregates.append(Aggregate(
                    name=agg_data["name"],
                    description=agg_data.get("description", ""),
                    attributes=[Attribute(**a) for a in agg_data.get("attributes", [])],
                    behaviors=agg_data.get("behaviors", [])
                ))
            
            value_objects = []
            for vo_data in domain.get("value_objects", []):
                value_objects.append(ValueSpec(
                    name=vo_data["name"],
                    description=vo_data.get("description", ""),
                    attributes=[Attribute(**a) for a in vo_data.get("attributes", [])]
                ))
                
            services = []
            for svc_data in domain.get("services", []):
                services.append(self._parse_service(svc_data))
                
            ports = []
            for port_data in domain.get("ports", []):
                ports.append(self._parse_port(port_data))
                
            use_cases = []
            for uc_data in app.get("use_cases", []):
                use_cases.append(self._parse_use_case(uc_data))
                
            self.contexts.append(BoundedContext(
                name=ctx_data["name"],
                description=ctx_data.get("description", ""),
                aggregates=aggregates,
                value_objects=value_objects,
                services=services,
                ports=ports,
                use_cases=use_cases
            ))

    def _parse_operation(self, op_data: Dict[str, Any]) -> Operation:
        return Operation(
            name=op_data["name"],
            description=op_data.get("description", ""),
            inputs=[Attribute(**a) for a in op_data.get("inputs", [])],
            output_type=op_data.get("output", {}).get("type", "None")
        )

    def _parse_service(self, svc_data: Dict[str, Any]) -> Service:
        return Service(
            name=svc_data["name"],
            description=svc_data.get("description", ""),
            operations=[self._parse_operation(op) for op in svc_data.get("operations", [])]
        )

    def _parse_port(self, port_data: Dict[str, Any]) -> Port:
        return Port(
            name=port_data["name"],
            description=port_data.get("description", ""),
            kind=port_data.get("kind", "gateway"),
            operations=[self._parse_operation(op) for op in port_data.get("operations", [])]
        )

    def _parse_use_case(self, uc_data: Dict[str, Any]) -> UseCase:
        cmd_data = uc_data.get("command", {"name": f"{uc_data['name']}Command", "attributes": []})
        res_data = uc_data.get("result", {"name": f"{uc_data['name']}Result", "attributes": []})
        
        command = Command(
            name=cmd_data["name"],
            attributes=[Attribute(**a) for a in cmd_data.get("attributes", [])]
        )
        result = Result(
            name=res_data["name"],
            attributes=[Attribute(**a) for a in res_data.get("attributes", [])]
        )
        
        depends_on = uc_data.get("depends_on", {})
        return UseCase(
            name=uc_data["name"],
            kind=uc_data.get("kind", "command"),
            description=uc_data.get("description", ""),
            command=command,
            result=result,
            depends_on_services=depends_on.get("services", []),
            depends_on_ports=depends_on.get("ports", [])
        )
