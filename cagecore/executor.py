"""
Executor (applies diffs only)
Executes planned changes using diff-based operations.
"""

from . import referee, logbook, workbench, planner, diffs, tests

# Global flag to track when diff mode is active
DIFF_MODE_ACTIVE = False


def apply_latest_plan():
    """Apply the latest plan using diff-based operations"""
    plan = planner.get_latest_plan()
    if not plan:
        return {"success": False, "error": "No plan to execute"}

    try:
        # Read the current file content
        filename = plan["target_file"]
        if workbench.file_exists(filename):
            original_content = workbench.read_file(filename)
        else:
            original_content = ""

        # Generate new content
        new_content = original_content.replace(plan["find_text"], plan["replace_text"])

        # Create unified diff
        diff_result = diffs.create_diff(original_content, new_content, filename)

        # Log the diff
        logbook.append("diff", {
            "plan_title": plan["title"],
            "file": filename,
            "diff": diff_result["diff"]
        })

        # Apply the diff
        apply_result = diffs.apply_diff(filename, original_content, new_content)

        # Log the apply result
        logbook.append("apply_result", {
            "plan_title": plan["title"],
            "file": filename,
            "success": apply_result["success"],
            "error": apply_result.get("error")
        })

        if not apply_result["success"]:
            return {"success": False, "error": apply_result.get("error", "Apply failed")}

        # Run tests
        test_result = tests.run_tests(filename)

        # Log test results
        logbook.append("tests", {
            "plan_title": plan["title"],
            "file": filename,
            "passed": test_result["passed"],
            "details": test_result["details"]
        })

        if not test_result["passed"]:
            # Revert on test failure
            revert_result = diffs.apply_diff(filename, new_content, original_content)
            logbook.append("revert", {
                "plan_title": plan["title"],
                "file": filename,
                "reason": "test_failure",
                "revert_success": revert_result["success"]
            })
            return {"success": False, "error": "Tests failed, changes reverted"}

        # Clear the plan after successful execution
        planner.clear_current_plan()

        return {"success": True}

    except Exception as e:
        error_msg = str(e)
        logbook.append("apply_error", {
            "plan_title": plan["title"],
            "error": error_msg
        })
        return {"success": False, "error": error_msg}