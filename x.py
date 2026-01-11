from codegen.python_gen.domain.value_objects.class_spec import ClassSpec


def main():
    spec = ClassSpec.create(
        name="my_class", description="A class for testing purposes."
    )
    print(spec.name)


if __name__ == "__main__":
    main()
