from app.engine import WorkflowEngine
from app.models import WorkflowRequest


def test_workflow_requires_approval_when_kyc_document_missing() -> None:
    response = WorkflowEngine().run(
        "workflow-1",
        WorkflowRequest(
            customer_name="Adebayo Foods Limited",
            documents=["certificate_of_incorporation", "director_id"],
            requested_products=["business_account"],
            voice_channel=True,
        ),
    )

    assert response.approval_required is True
    assert response.status == "approval_required"
    assert response.completion_percentage == 72
    assert any(step.agent == "VoiceAgent" for step in response.steps)


def test_workflow_auto_approves_complete_low_risk_case() -> None:
    response = WorkflowEngine().run(
        "workflow-2",
        WorkflowRequest(
            customer_name="Blue River Limited",
            risk_level="low",
            documents=[
                "certificate_of_incorporation",
                "director_id",
                "proof_of_address",
            ],
        ),
    )

    assert response.approval_required is False
    assert response.status == "completed"
    assert response.completion_percentage == 100
