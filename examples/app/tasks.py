import random
import time
from typing import Any, Dict


from app.celery import celery_app


@celery_app.task(name="celery.process_data")
def process_data_task(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate data processing task with progress updates
    """
    total_items = data.get("item_count", 10)
    processing_time = data.get("processing_time", 2)  # seconds per item

    try:
        results = []
        for i in range(total_items):
            # Simulate processing time
            time.sleep(processing_time)

            # Simulate some processing result
            result = {
                "item_id": i + 1,
                "processed_value": random.randint(1, 100),
                "timestamp": time.time(),
            }
            results.append(result)

        return {
            "status": "completed",
            "total_processed": len(results),
            "results": results,
            "summary": {
                "avg_value": sum(r["processed_value"] for r in results) / len(results),
                "max_value": max(r["processed_value"] for r in results),
                "min_value": min(r["processed_value"] for r in results),
            },
        }

    except Exception as exc:
        raise exc


@celery_app.task(name="mail.send_email")
def send_email_task(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate email sending task
    """
    try:
        # Simulate email sending delay
        time.sleep(email_data.get("processing_time", 10))

        # Simulate random failures (10% chance)
        if random.random() < 0.1:
            raise Exception("SMTP server temporarily unavailable")

        return {
            "status": "sent",
            "recipient": email_data.get("to"),
            "subject": email_data.get("subject"),
            "sent_at": time.time(),
            "message_id": f"msg_{random.randint(1000, 9999)}",
        }

    except Exception as exc:
        raise exc
