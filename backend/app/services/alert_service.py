import json
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models import Alert, WaterSource

logger = logging.getLogger("aquashield.alerts")

class AlertService:
    @staticmethod
    async def trigger_danger_alert(db: AsyncSession, source: WaterSource, prediction_result: dict) -> Alert:
        """
        Creates an alert in the database when a source turns Dangerous or exceeds critical safety thresholds.
        Dispatches stub notification to external notification hooks (Email/SMS).
        """
        severity = "critical" if prediction_result["classification"] == "Dangerous" else "warning"
        title = f"Alert: {source.name} is classified as {prediction_result['classification']}"
        message = (
            f"Sensor readings for '{source.name}' indicate {prediction_result['classification']} condition. "
            f"Recommendation: {prediction_result['recommendation']}. "
            f"Action: {', '.join(prediction_result['action_steps'][:2])}"
        )

        alert = Alert(
            source_id=source.id,
            source_name=source.name,
            title=title,
            message=message,
            severity=severity,
            status="active",
            parameters_json=json.dumps(prediction_result["inputs"]),
            created_at=datetime.utcnow()
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)

        # Dispatch stub external notifications
        AlertService._dispatch_stub_notifications(alert, source)
        return alert

    @staticmethod
    def _dispatch_stub_notifications(alert: Alert, source: WaterSource):
        """
        Stub integration for Email / SMS / Webhook notification.
        """
        logger.info(
            f"[NOTIFICATION STUB - SMS] Emergency broadcast to zone '{source.zone}': {alert.title}. "
            f"Call operator: {source.contact_phone}"
        )
        logger.info(
            f"[NOTIFICATION STUB - EMAIL] Sent alert email to municipal water authority: {alert.message}"
        )

alert_service = AlertService()
