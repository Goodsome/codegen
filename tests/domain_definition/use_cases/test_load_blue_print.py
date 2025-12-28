from codegen.domain_definition.domain.value_objects.blueprint import Blueprint


def test_load_blueprint(local_blueprint: Blueprint) -> None:
    print(local_blueprint.model_dump_json(indent=2))
