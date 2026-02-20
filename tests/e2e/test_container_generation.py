import pytest
from pathlib import Path
from codegen.entrypoints.cli.application import app

def test_container_generation_default(cli_runner, working_dir, monkeypatch):
    """
    Scenario: Generating container.py by default
    Given: A blueprint with a valid context, domain, ports, and implementations but NO container spec
    When: Running 'codegen build'
    Then: container.py is generated correctly and binds the first implementation to the port.
    """
    project_name = "AutoContainerProject"
    project_dir = "auto_container_project"
    blueprint_content = """
name: "AutoContainerProject"
description: "Test auto generation of container"

contexts:
  - name: "Core"
    domain:
      ports:
        - name: "NotificationPort"
          kind: "adapter"
          operations:
            - name: "send_notification"
              inputs:
                - name: "message"
                  type: "str"
              output:
                type: "None"
    
    infrastructure:
      implementations:
        - name: "EmailNotificationAdapter"
          implements: "NotificationPort"
          technology: "email"
          description: "Sends notification via email"
        - name: "SMSNotificationAdapter"
          implements: "NotificationPort"
          technology: "sms"
          description: "Sends notification via SMS"
"""
    blueprint_file = working_dir / "codegen.yaml"
    blueprint_file.write_text(blueprint_content)

    monkeypatch.chdir(working_dir)

    result = cli_runner.invoke(app, ["build"])

    assert result.exit_code == 0

    project_root = working_dir
    container_file = project_root / "src" / "auto_container_project" / "core" / "container.py"
    
    # Verify container.py exists
    assert container_file.exists()

    content = container_file.read_text()
    
    assert "from auto_container_project.core.infrastructure.adapters import EmailNotificationAdapter" in content
    
    # Verify the Container class is generated
    assert "class Container(DeclarativeContainer):" in content
    
    # Verify the first implementation was chosen for the port
    assert "email_notification_adapter = Factory(EmailNotificationAdapter)" in content
    assert "EmailNotificationAdapter" in content

    # Ensure SMS is NOT the default chosen provider for this port
    assert "SMSNotificationAdapter" not in content

