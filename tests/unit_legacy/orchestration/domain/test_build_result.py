from codegen.orchestration.domain.enums import BuildStatus, FileStatus
from codegen.orchestration.domain.value_objects.build_result import BuildResult
from codegen.orchestration.domain.value_objects.build_stats import BuildStats
from codegen.orchestration.domain.value_objects.file_result import FileResult

def test_build_stats_add_result():
    stats = BuildStats(
        total_files=0,
        created_count=0,
        updated_count=0,
        skipped_count=0,
        failed_count=0,
        duration_ms=0
    )
    
    # Test CREATED
    stats.add_result(FileResult(path="a.py", status=FileStatus.CREATED))
    assert stats.total_files == 1
    assert stats.created_count == 1
    
    # Test UPDATED
    stats.add_result(FileResult(path="b.py", status=FileStatus.UPDATED))
    assert stats.total_files == 2
    assert stats.updated_count == 1
    
    # Test SKIPPED
    stats.add_result(FileResult(path="c.py", status=FileStatus.SKIPPED))
    assert stats.total_files == 3
    assert stats.skipped_count == 1
    
    # Test FAILED
    stats.add_result(FileResult(path="d.py", status=FileStatus.FAILED))
    assert stats.total_files == 4
    assert stats.failed_count == 1

def test_build_result_add_file_result():
    result = BuildResult(
        status=BuildStatus.SUCCESS,
        files=[],
        stats=BuildStats(
            total_files=0,
            created_count=0,
            updated_count=0,
            skipped_count=0,
            failed_count=0,
            duration_ms=0
        ),
        messages=[]
    )
    
    # Adding a SUCCESS file
    result.add_file_result(FileResult(path="a.py", status=FileStatus.CREATED))
    assert len(result.files) == 1
    assert result.status == BuildStatus.SUCCESS
    assert result.stats.created_count == 1
    
    # Adding a FAILED file should change status to WARNING
    result.add_file_result(FileResult(path="b.py", status=FileStatus.FAILED))
    assert len(result.files) == 2
    assert result.status == BuildStatus.WARNING
    assert result.stats.failed_count == 1
