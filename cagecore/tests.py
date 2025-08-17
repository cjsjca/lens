
"""
Tests (smoke/guard checks)
Minimal testing to verify changes are safe and correct.
"""

from . import workbench


_last_test_result = None


def run_tests(filename):
    """Run basic smoke tests on a file"""
    global _last_test_result
    
    try:
        # Test 1: File exists and is readable
        if not workbench.file_exists(filename):
            _last_test_result = {"passed": False, "details": "File does not exist"}
            return _last_test_result
        
        content = workbench.read_file(filename)
        
        # Test 2: Content is valid UTF-8 (already checked by read_file)
        
        # Test 3: No TODO markers left
        if "TODO" in content:
            _last_test_result = {"passed": False, "details": "TODO markers found in content"}
            return _last_test_result
        
        # Test 4: File is not empty
        if not content.strip():
            _last_test_result = {"passed": False, "details": "File is empty"}
            return _last_test_result
        
        _last_test_result = {"passed": True, "details": "All smoke tests passed"}
        return _last_test_result
        
    except Exception as e:
        _last_test_result = {"passed": False, "details": f"Test error: {str(e)}"}
        return _last_test_result


def last_tests_passed():
    """Check if the last test run passed"""
    global _last_test_result
    return _last_test_result is not None and _last_test_result.get("passed", False)
