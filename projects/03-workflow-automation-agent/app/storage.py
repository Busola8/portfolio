from __future__ import annotations

from collections import deque

from .models import WorkflowResponse


class WorkflowStore:
    def __init__(self) -> None:
        self.items: deque[WorkflowResponse] = deque(maxlen=50)

    def save(self, response: WorkflowResponse) -> None:
        self.items.appendleft(response)

    def summary(self) -> dict:
        if not self.items:
            return {
                "total_workflows": 0,
                "auto_approved": 0,
                "approval_required": 0,
                "average_completion": 0,
                "latest": [],
            }
        total = len(self.items)
        approval_required = sum(1 for item in self.items if item.approval_required)
        return {
            "total_workflows": total,
            "auto_approved": total - approval_required,
            "approval_required": approval_required,
            "average_completion": round(
                sum(item.completion_percentage for item in self.items) / total,
                1,
            ),
            "latest": [
                {
                    "workflow_id": item.workflow_id,
                    "status": item.status,
                    "approval_required": item.approval_required,
                    "completion_percentage": item.completion_percentage,
                    "summary": item.summary,
                }
                for item in list(self.items)[:5]
            ],
        }
