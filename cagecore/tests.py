
"""
Tests (smoke/guard checks)
Provides basic validation for applied changes.
"""

from . import workbench, logbook

# Module-level storage for last test result
_last_test_result = None


def run_tests(filename):
    """Run smoke tests on a file after changes"""
    global _last_test_result
    
    try:
        # Check if file exists
        if not workbench.file_exists(filename):
            _last_test_result = {
                "passed": False,
                "details": f"File {filename} does not exist"
            }
            return _last_test_result
        
        # Read file content
        content = workbench.read_file(filename)
        
        # Check if file is non-empty
        if not content.strip():
            _last_test_result = {
                "passed": False,
                "details": f"File {filename} is empty"
            }
            return _last_test_result
        
        # Check if content is valid UTF-8 (already handled by read_file)
        # Additional basic checks could go here
        
        _last_test_result = {
            "passed": True,
            "details": f"File {filename} passed basic validation"
        }
        return _last_test_result
        
    except Exception as e:
        _last_test_result = {
            "passed": False,
            "details": f"Test error: {str(e)}"
        }
        return _last_test_result


def last_tests_passed():
    """Check if the last tests passed"""
    return _last_test_result is not None and _last_test_result.get("passed", False)
