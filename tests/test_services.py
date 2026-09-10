"""
Unit and integration tests for Vymed services:
- Fee Bump sponsored transaction service (VH-B01)
- GS1 DataMatrix barcode parsing & cryptographic hash verification (VH-B02)
- Distributor alias manager with Ed25519 signature verification (VH-B04)
- Geographic counterfeit anomaly detection (VH-B05)
- Token bucket rate limiter (VH-B06)
"""

from datetime import date
import pytest
from stellar_sdk import Account, Asset, Keypair, Network, TransactionBuilder

from src.services.anomaly_detector import GeographicAnomalyDetector
from src.services.gs1_service import GS1ParserService
from src.services.rate_limiter import RateLimiter
from src.services.stellar_service import StellarService


# --------------------------------------------------------------------------
# VH-B01: Fee-Bump Sponsored Transactions
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_fee_bump_transaction_sponsorship():
    """Verify that create_fee_bump_transaction signs and wraps inner tx in FeeBump envelope."""
    service = StellarService()

    # Generate test inner transaction
    user_kp = Keypair.random()
    account = Account(user_kp.public_key, 1)
    inner_tx = (
        TransactionBuilder(account, service.network_passphrase, 100)
        .set_timeout(30)
        .append_payment_op(destination=user_kp.public_key, asset=Asset.native(), amount="0.0000001")
        .build()
    )
    inner_tx.sign(user_kp)
    inner_xdr = inner_tx.to_xdr()

    # Fee Bump wrapping
    fee_bump_xdr = await service.create_fee_bump_transaction(inner_xdr, base_fee=200)

    assert isinstance(fee_bump_xdr, str)
    assert len(fee_bump_xdr) > len(inner_xdr)


# --------------------------------------------------------------------------
# VH-B02: GS1 DataMatrix Barcode Parsing & Hash Verification
# --------------------------------------------------------------------------

def test_gs1_bracketed_barcode_parsing():
    """Verify parsing of human-readable GS1 bracketed format."""
    raw = "(01)00301234567896(21)SER12345(17)281231(10)LOT9988"
    result = GS1ParserService.parse_barcode(raw)

    assert result.gtin == "00301234567896"
    assert result.serial_number == "SER12345"
    assert result.expiry_date_str == "281231"
    assert result.expiry_date == date(2028, 12, 31)
    assert result.batch_number == "LOT9988"
    assert not result.is_expired
    assert len(result.cryptographic_hash) == 64  # SHA-256


def test_gs1_fnc1_stream_parsing():
    """Verify parsing of FNC1 stream delimited barcodes."""
    raw = "010030123456789617290101\x1d21SN771122\x1d10BATCHA"
    result = GS1ParserService.parse_barcode(raw)

    assert result.gtin == "00301234567896"
    assert result.expiry_date_str == "290101"
    assert result.serial_number == "SN771122"
    assert result.batch_number == "BATCHA"


def test_gs1_expired_barcode():
    """Verify expired barcode triggers is_expired flag."""
    raw = "(01)00301234567896(21)SEROLD(17)200101(10)LOTOLD"
    result = GS1ParserService.parse_barcode(raw)
    assert result.is_expired is True

    verify_res = GS1ParserService.verify_barcode(raw)
    assert verify_res["verification_status"] == "expired"


# --------------------------------------------------------------------------
# VH-B05: Geographic Counterfeit Anomaly Detection
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_geographic_anomaly_impossible_speed():
    """Verify that scans separated by distant geography within short time trigger anomaly."""
    detector = GeographicAnomalyDetector()
    unit_id = "AMOX-SERIAL-TEST-01"

    # Scan 1: London (51.5074, -0.1278) at t=0
    res1 = await detector.record_and_evaluate_scan(
        unit_id=unit_id,
        latitude=51.5074,
        longitude=-0.1278,
        timestamp=1000.0,
    )
    assert res1["is_anomaly"] is False

    # Scan 2: New York (40.7128, -74.0060) 10 minutes later (t=1600) -> 5500 km in 10 mins
    res2 = await detector.record_and_evaluate_scan(
        unit_id=unit_id,
        latitude=40.7128,
        longitude=-74.0060,
        timestamp=1600.0,
    )
    assert res2["is_anomaly"] is True
    assert res2["anomaly_type"] in ("IMPOSSIBLE_TRANSIT_VELOCITY", "DUPLICATE_CONCURRENT_SCAN")


@pytest.mark.asyncio
async def test_geographic_anomaly_plausible_scan():
    """Verify that local scans within reasonable time window do not trigger anomaly."""
    detector = GeographicAnomalyDetector()
    unit_id = "AMOX-SERIAL-TEST-02"

    # Scan 1: Clinic A in Lagos (6.5244, 3.3792) at t=0
    res1 = await detector.record_and_evaluate_scan(
        unit_id=unit_id,
        latitude=6.5244,
        longitude=3.3792,
        timestamp=1000.0,
    )
    assert res1["is_anomaly"] is False

    # Scan 2: Pharmacy B 2 km away, 30 minutes later (t=2800)
    res2 = await detector.record_and_evaluate_scan(
        unit_id=unit_id,
        latitude=6.5300,
        longitude=3.3850,
        timestamp=2800.0,
    )
    assert res2["is_anomaly"] is False


# --------------------------------------------------------------------------
# VH-B06: Token Bucket Rate Limiter
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_token_bucket_exhaustion():
    """Verify that token-bucket rate limiter throttles once capacity is depleted."""
    limiter = RateLimiter(default_capacity=3, refill_rate_per_sec=0.1)
    bucket_key = "test_ip_127_0_0_1"

    # Consume 3 tokens
    ok1, _ = await limiter.consume_token(bucket_key)
    ok2, _ = await limiter.consume_token(bucket_key)
    ok3, _ = await limiter.consume_token(bucket_key)
    assert ok1 and ok2 and ok3

    # 4th request should be throttled
    ok4, remaining = await limiter.consume_token(bucket_key)
    assert ok4 is False
    assert remaining < 1.0
