from codegen.entrypoints.cli.application import app

def test_codegen_init_happy_path(cli_runner, tmp_path, monkeypatch):
    """
    Scenario: Standard DDD Project Initialization
    Given: An empty directory
    When: Running 'codegen init'
    Then: The codegen.yaml blueprint is created correctly with a Shared context.
    """
    monkeypatch.chdir(tmp_path)
    
    result = cli_runner.invoke(app, ["init"])
    
    assert result.exit_code == 0
    assert "Success" in result.stdout
    
    blueprint_file = tmp_path / "codegen.yaml"
    assert blueprint_file.exists()
    
    content = blueprint_file.read_text()
    assert "Shared" in content
    # The default blueprint is saved

def test_codegen_init_already_exists(cli_runner, tmp_path, monkeypatch):
    """
    Scenario: Blueprint already exists
    Given: A directory with an existing codegen.yaml
    When: Running 'codegen init'
    Then: It should abort and not overwrite.
    """
    monkeypatch.chdir(tmp_path)
    
    blueprint_file = tmp_path / "codegen.yaml"
    blueprint_file.write_text("existing content")
    
    result = cli_runner.invoke(app, ["init"])
    
    assert result.exit_code == 1
    assert "already exists" in result.stdout
    
    content = blueprint_file.read_text()
    assert content == "existing content"

def test_codegen_init_and_build(cli_runner, tmp_path, monkeypatch):
    """
    Scenario: Init and immediately build
    Given: An empty directory
    When: Running 'codegen init' then 'codegen build'
    Then: It should generate the project scaffolding successfully.
    """
    monkeypatch.chdir(tmp_path)
    
    # Run init
    init_result = cli_runner.invoke(app, ["init"])
    assert init_result.exit_code == 0
    
    # Run build
    build_result = cli_runner.invoke(app, ["build"])
    assert build_result.exit_code == 0
    
    assert (tmp_path / "src").exists()
    
    src_dirs = list((tmp_path / "src").iterdir())
    assert len(src_dirs) > 0
    
    # We should also see a "shared" directory inside the project module
    project_module_dir = next(d for d in src_dirs if d.is_dir() and not d.name.startswith("."))
    assert (project_module_dir / "shared").exists()
