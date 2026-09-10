"""
Geographic Counterfeit Anomaly Detection & Alert Webhook Service (VH-B05)

Analyzes medication scan location clusters to detect impossible transit velocities
and simultaneous duplicate scans across geographically distant points.
Triggers alert webhooks when counterfeit anomalies are detected.
"""

from dataclasses import dataclass
import logging
import math
import time
from typing import Any, Dict, List, Optional
import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ScanLocation:
    unit_id: str
    latitude: float
    longitude: float
    timestamp: float


class GeographicAnomalyDetector:
    """
    Detector for geographical counterfeit scan anomalies.
    """

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or settings.ALERT_WEBHOOK_URL
        # In-memory store for unit scan histories: unit_id -> List[ScanLocation]
        self._scan_history: Dict[str, List[ScanLocation]] = {}
        # Max velocity threshold (km/h) for plausible ground/commercial travel
        self.max_velocity_kmh = 900.0

    @staticmethod
    def calculate_haversine_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """
        Calculate Great Circle distance in kilometers using the Haversine formula.
        """
        r_earth = 6371.0  # Earth radius in kilometers

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r_earth * c

    async def record_and_evaluate_scan(
        self,
        unit_id: str,
        latitude: float,
        longitude: float,
        timestamp: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Record a scan event, evaluate spatial-temporal plausibility,
        and trigger alert webhook if anomalous.
        """
        current_time = timestamp if timestamp is not None else time.time()
        new_scan = ScanLocation(
            unit_id=unit_id,
            latitude=latitude,
            longitude=longitude,
            timestamp=current_time,
        )

        history = self._scan_history.setdefault(unit_id, [])

        is_anomaly = False
        anomaly_type: Optional[str] = None
        anomaly_details: Dict[str, Any] = {}

        if history:
            prev_scan = history[-1]
            distance_km = self.calculate_haversine_distance(
                prev_scan.latitude,
                prev_scan.longitude,
                latitude,
                longitude,
            )
            time_delta_seconds = max(current_time - prev_scan.timestamp, 0.0)
            time_delta_hours = time_delta_seconds / 3600.0

            if time_delta_hours > 0:
                speed_kmh = distance_km / time_delta_hours
            else:
                speed_kmh = float("inf") if distance_km > 0.1 else 0.0

            # Check 1: Concurrent scans in distant locations (< 2 minutes, > 50 km)
            if time_delta_seconds < 120 and distance_km > 50.0:
                is_anomaly = True
                anomaly_type = "DUPLICATE_CONCURRENT_SCAN"
                anomaly_details = {
                    "distance_km": round(distance_km, 2),
                    "time_delta_seconds": round(time_delta_seconds, 1),
                    "reason": "Identical unit scanned in distant locations simultaneously",
                }
            # Check 2: Impossible travel velocity
            elif distance_km > 25.0 and speed_kmh > self.max_velocity_kmh:
                is_anomaly = True
                anomaly_type = "IMPOSSIBLE_TRANSIT_VELOCITY"
                anomaly_details = {
                    "distance_km": round(distance_km, 2),
                    "speed_kmh": round(speed_kmh, 1),
                    "time_delta_hours": round(time_delta_hours, 3),
                    "reason": f"Implied transit speed {round(speed_kmh, 1)} km/h exceeds physical limit",
                }

        # Append to history
        history.append(new_scan)

        # Trigger webhook alert if anomaly detected
        alert_sent = False
        if is_anomaly:
            alert_sent = await self._send_alert_webhook(
                unit_id=unit_id,
                anomaly_type=anomaly_type or "COUNTERFEIT_ALERT",
                details=anomaly_details,
                location={"latitude": latitude, "longitude": longitude},
            )

        return {
            "unit_id": unit_id,
            "is_anomaly": is_anomaly,
            "anomaly_type": anomaly_type,
            "details": anomaly_details,
            "alert_webhook_sent": alert_sent,
        }

    async def _send_alert_webhook(
        self,
        unit_id: str,
        anomaly_type: str,
        details: Dict[str, Any],
        location: Dict[str, float],
    ) -> bool:
        """
        Dispatch POST alert payload to configured security webhook endpoint.
        """
        if not self.webhook_url:
            logger.warning(
                "Counterfeit anomaly detected for %s (%s), but ALERT_WEBHOOK_URL is not configured",
                unit_id,
                anomaly_type,
            )
            return False

        payload = {
            "event": "counterfeit_anomaly_detected",
            "unit_id": unit_id,
            "anomaly_type": anomaly_type,
            "location": location,
            "details": details,
            "timestamp": time.time(),
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(self.webhook_url, json=payload)
                return resp.status_code in (200, 201, 202, 204)
        except Exception as e:
            logger.error("Failed to deliver alert webhook: %s", str(e))
            return False
