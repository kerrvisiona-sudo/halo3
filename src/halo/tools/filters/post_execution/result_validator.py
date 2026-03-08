"""Result validator filter - validates tool execution results."""

from ..base import ToolFilter, FilterResult, FilterStage
import logging

logger = logging.getLogger(__name__)


class ResultValidator(ToolFilter):
    """Validates tool execution results.

    Ensures:
    - Result has required fields (status, message)
    - Status is valid ("completed", "pending", "error")
    - Device state is properly structured
    """

    def __init__(self):
        super().__init__("result_validator", FilterStage.POST_EXECUTION)

    def _do_filter(self, data: dict, context: dict) -> FilterResult:
        """Validate tool execution result.

        Args:
            data: Tool execution result dict
            context: Conversation context

        Returns:
            FilterResult (pass if valid, modify if corrected)
        """
        issues = []
        modified = False
        result = data.copy()

        # Check required fields
        if "status" not in result:
            issues.append("Missing 'status' field")
            result["status"] = "error"
            modified = True

        if "message" not in result:
            issues.append("Missing 'message' field")
            result["message"] = "No message provided"
            modified = True

        # Validate status value
        valid_statuses = ["completed", "pending", "error"]
        if result.get("status") not in valid_statuses:
            issues.append(f"Invalid status: {result.get('status')}")
            result["status"] = "error"
            modified = True

        # Ensure device_state exists
        if "device_state" not in result:
            result["device_state"] = {}
            modified = True

        # Check for error status but no error message
        if result.get("status") == "error" and not result.get("message"):
            result["message"] = "An error occurred"
            modified = True

        if issues:
            logger.warning(f"Result validation issues: {issues}")

        if modified:
            logger.info("Result corrected by validator")
            return FilterResult(
                action="modify",
                modified_data=result,
                metadata={
                    "validator": "result",
                    "issues_found": issues,
                    "corrected": True,
                },
            )

        return FilterResult(
            action="pass",
            metadata={"validator": "result", "valid": True},
        )
