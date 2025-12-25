from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


def test_parse():
    test_cases = [
        ("int", "int", []),
        ("list[int]", "list", ["int"]),
        ("dict[str, int]", "dict", ["str", "int"]),
        ("Optional[list[str]]", "Optional", ["list[str]"]),
        ("Union[dict[str, int], list[str]]", "Union", ["dict[str, int]", "list[str]"]),
        ("str | None", "Union", ["str", "None"]),
        # ("Callable[[int, str], None]", "Callable", ["[int, str]", "None"]),
    ]

    for annotation, expected_name, expected_subs in test_cases:
        spec = TypeAnnotationSpec.parse(annotation)
        assert spec.name == expected_name
        assert len(spec.args) == len(expected_subs)
        assert spec.render() == annotation
        for i, sub_expected in enumerate(expected_subs):
            assert spec.args[i].render() == sub_expected
        print(f"Passed: {annotation}")


if __name__ == "__main__":
    test_parse()
