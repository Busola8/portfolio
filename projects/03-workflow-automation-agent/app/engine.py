from __future__ import annotations

from .models import WorkflowRequest, WorkflowResponse, WorkflowStep


REQUIRED_KYC_DOCS = {"certificate_of_incorporation", "director_id", "proof_of_address"}


class WorkflowEngine:
    """Local n8n/CrewAI-style workflow runner for portfolio demo use."""

    def run(self, workflow_id: str, request: WorkflowRequest) -> WorkflowResponse:
        steps: list[WorkflowStep] = []
        docs = set(request.documents)
        missing_docs = sorted(REQUIRED_KYC_DOCS - docs)
        high_risk = request.risk_level.lower() in {"high", "critical"}
        approval_required = bool(missing_docs or high_risk)

        steps.append(
            WorkflowStep(
                agent="IntakeAgent",
                action="Capture onboarding request",
                status="completed",
                details=f"Created onboarding case for {request.customer_name} in {request.country}.",
            )
        )
        steps.append(
            WorkflowStep(
                agent="KYCAgent",
                action="Validate KYC requirements",
                status="review" if missing_docs else "completed",
                details=(
                    f"Missing documents: {', '.join(missing_docs)}."
                    if missing_docs
                    else "All required KYC documents are present."
                ),
            )
        )
        steps.append(
            WorkflowStep(
                agent="DocumentAgent",
                action="Create document workspace",
                status="completed",
                details=f"Prepared SharePoint folder {request.sharepoint_folder or '/Onboarding/Generated'} and document checklist.",
            )
        )
        steps.append(
            WorkflowStep(
                agent="ApprovalAgent",
                action="Route approval",
                status="pending" if approval_required else "auto-approved",
                details=(
                    "Sent to Compliance Approval Queue."
                    if approval_required
                    else "Customer qualifies for straight-through onboarding."
                ),
            )
        )
        if request.voice_channel:
            steps.append(
                WorkflowStep(
                    agent="VoiceAgent",
                    action="Prepare voice follow-up",
                    status="scheduled",
                    details="Generated telephony script for missing KYC or approval status update.",
                )
            )
        steps.append(
            WorkflowStep(
                agent="NotificationAgent",
                action="Notify stakeholders",
                status="completed",
                details="Sent workflow status to operations, compliance, and relationship manager channels.",
            )
        )

        completion = 72 if approval_required else 100
        documents_created = [
            "onboarding_case.json",
            "kyc_checklist.md",
            "approval_summary.md",
        ]
        notifications = [
            "Relationship manager notified",
            "Compliance queue updated" if approval_required else "Operations notified of auto-approval",
        ]
        return WorkflowResponse(
            workflow_id=workflow_id,
            status="approval_required" if approval_required else "completed",
            approval_required=approval_required,
            assigned_queue="Compliance Approval Queue" if approval_required else "Operations Fulfillment",
            completion_percentage=completion,
            summary=(
                f"{request.customer_name} onboarding is "
                f"{'waiting for compliance approval' if approval_required else 'ready for fulfillment'}."
            ),
            steps=steps,
            documents_created=documents_created,
            notifications=notifications,
            n8n_replacement_notes=[
                "IntakeAgent maps to an n8n Webhook trigger.",
                "KYCAgent maps to document validation and API enrichment nodes.",
                "DocumentAgent maps to SharePoint create-folder/upload nodes.",
                "ApprovalAgent maps to an n8n Wait/approval workflow.",
                "VoiceAgent maps to Twilio or telephony integration nodes.",
            ],
        )
