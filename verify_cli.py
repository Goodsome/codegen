from typer.testing import CliRunner
from codegen.cli.application import app
import traceback

runner = CliRunner()

def run_command(args, ignore_error=False):
    print(f"Executing: codegen {' '.join(args)}")
    result = runner.invoke(app, args)
    print(result.stdout)
    if result.exit_code != 0 and not ignore_error:
        print(f"❌ Command failed with exit code {result.exit_code}")
        if result.exception:
            print(f"Exception: {result.exception}")
            traceback.print_tb(result.exc_info[2])
    return result

def test_commands():
    print("\nTesting Commands...")
    
    # 0. Cleanup (if exists)
    run_command(["delete", "context", "UCTestContext"], ignore_error=True)
    
    # 1. Add Context (Setup)
    res = run_command(["add", "context", "UCTestContext", "--desc", "Context for UC Testing"])
    if res.exit_code != 0:
         print("Context creation failed, possibly due to race condition or concurrent access. Retrying cleanup...")
         run_command(["delete", "context", "UCTestContext"], ignore_error=True)
         res = run_command(["add", "context", "UCTestContext", "--desc", "Context for UC Testing"])
         assert res.exit_code == 0

    # 2. Add Use Case
    res = run_command([
        "add", "use-case", "TestUseCase", 
        "--context", "UCTestContext", 
        "--kind", "command", 
        "--desc", "A test use case"
    ])
    assert res.exit_code == 0
    assert "✅ Use Case 'TestUseCase' (command) added" in res.stdout

    # 3. Update Use Case
    res = run_command([
        "update", "use-case", "TestUseCase",
        "--context", "UCTestContext",
        "--desc", "Updated description"
    ])
    assert res.exit_code == 0
    assert "✅ Use Case 'TestUseCase' updated" in res.stdout

    # 4. Delete Use Case
    res = run_command([
        "delete", "use-case", "TestUseCase",
        "--context", "UCTestContext"
    ])
    assert res.exit_code == 0
    assert "✅ Use_case 'TestUseCase' deleted" in res.stdout
    
    # 5. Cleanup Context
    run_command(["delete", "context", "UCTestContext"])

if __name__ == "__main__":
    try:
        test_commands()
        print("\n✅ Verification Successful!")
    except AssertionError as e:
        print(f"\n❌ Verification Failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        traceback.print_exc()
        exit(1)
