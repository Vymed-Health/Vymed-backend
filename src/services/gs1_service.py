"""
GS1 DataMatrix Barcode Parser & Cryptographic Hash Verification Service (VH-B02)

Parses GS1 standard Application Identifiers:
- AI (01): GTIN (Global Trade Item Number, 14 digits)
- AI (21): Serial Number (up to 20 alphanumeric characters)
- AI (17): Expiration Date (YYMMDD)
- AI (10): Batch / Lot Number (up to 20 alphanumeric characters)

Generates canonical cryptographic hashes (SHA-256) for on-chain anchoring
and validation against smart contract registries.
"""

from dataclasses import dataclass
from datetime import date, datetime
import hashlib
import re
from typing import Any, Dict, Optional


@dataclass
class GS1DataMatrix:
    """Parsed GS1 DataMatrix elements."""
    gtin: str
    serial_number: str
    expiry_date_str: str
    expiry_date: Optional[date]
    batch_number: str
    raw_barcode: str
    cryptographic_hash: str
    is_expired: bool


class GS1ParserService:
    """
    Service for parsing GS1 barcodes and calculating cryptographic verification hashes.
    """

    @staticmethod
    def compute_canonical_hash(
        gtin: str,
        serial_number: str,
        batch_number: str,
        expiry_date_str: str,
    ) -> str:
        """
        Compute deterministic SHA-256 hash across canonical GS1 attributes.
        """
        canonical = f"GTIN:{gtin}|SERIAL:{serial_number}|BATCH:{batch_number}|EXP:{expiry_date_str}"
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @classmethod
    def parse_barcode(cls, raw_data: str) -> GS1DataMatrix:
        """
        Parse a GS1 DataMatrix barcode string into structured components.

        Supports:
        - Human-readable bracketed format: '(01)00301234567896(21)SER123(17)281231(10)LOT456'
        - Raw element string with FNC1 (ASCII 29 \\x1d) or delimiter separators
        """
        cleaned = raw_data.strip()
        gtin = ""
        serial_number = ""
        expiry_date_str = ""
        batch_number = ""

        # Format 1: Bracketed AI syntax, e.g. (01)...(21)...
        if "(" in cleaned and ")" in cleaned:
            ai_pattern = re.compile(r"\((\d{2,4})\)([^()]+)")
            matches = ai_pattern.findall(cleaned)
            for ai, val in matches:
                val = val.strip()
                if ai == "01":
                    gtin = val
                elif ai == "21":
                    serial_number = val
                elif ai == "17":
                    expiry_date_str = val
                elif ai == "10":
                    batch_number = val
        else:
            # Format 2: Stream format with ASCII \x1d (GS) or delimiter |
            # AI 01 is fixed 14 digits, AI 17 is fixed 6 digits.
            stream = cleaned.replace("^", "\x1d").replace("|", "\x1d")
            tokens = stream.split("\x1d")

            for token in tokens:
                idx = 0
                while idx < len(token):
                    # Check for 01 (GTIN)
                    if token[idx:idx + 2] == "01" and len(token) >= idx + 16:
                        gtin = token[idx + 2:idx + 16]
                        idx += 16
                    # Check for 17 (Expiration Date)
                    elif token[idx:idx + 2] == "17" and len(token) >= idx + 8:
                        expiry_date_str = token[idx + 2:idx + 8]
                        idx += 8
                    # Check for 21 (Serial Number) - variable length, consumes rest of token
                    elif token[idx:idx + 2] == "21":
                        serial_number = token[idx + 2:]
                        break
                    # Check for 10 (Batch Number) - variable length, consumes rest of token
                    elif token[idx:idx + 2] == "10":
                        batch_number = token[idx + 2:]
                        break
                    else:
                        idx += 1

        if not gtin:
            # Fallback: simple colon or hyphen format or regex extract
            gtin_match = re.search(r"\b\d{14}\b", cleaned)
            if gtin_match:
                gtin = gtin_match.group(0)

        # Parse expiry date object (YYMMDD)
        parsed_date = None
        is_expired = False
        if expiry_date_str and len(expiry_date_str) == 6:
            try:
                # 20YY-MM-DD
                year = 2000 + int(expiry_date_str[0:2])
                month = int(expiry_date_str[2:4])
                day = int(expiry_date_str[4:6])
                if day == 0:
                    day = 28
                parsed_date = date(year, month, day)
                is_expired = parsed_date < date.today()
            except (ValueError, IndexError):
                pass

        crypto_hash = cls.compute_canonical_hash(
            gtin=gtin,
            serial_number=serial_number,
            batch_number=batch_number,
            expiry_date_str=expiry_date_str,
        )

        return GS1DataMatrix(
            gtin=gtin,
            serial_number=serial_number,
            expiry_date_str=expiry_date_str,
            expiry_date=parsed_date,
            batch_number=batch_number,
            raw_barcode=raw_data,
            cryptographic_hash=crypto_hash,
            is_expired=is_expired,
        )

    @classmethod
    def verify_barcode(
        cls,
        raw_barcode: str,
        expected_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Verify barcode syntax, expiration, and cryptographic integrity.
        """
        parsed = cls.parse_barcode(raw_barcode)
        hash_valid = (
            expected_hash is None or parsed.cryptographic_hash.lower() == expected_hash.lower()
        )

        valid_syntax = bool(parsed.gtin and (parsed.serial_number or parsed.batch_number))

        return {
            "valid_syntax": valid_syntax,
            "gtin": parsed.gtin,
            "serial_number": parsed.serial_number,
            "batch_number": parsed.batch_number,
            "expiry_date": parsed.expiry_date.isoformat() if parsed.expiry_date else None,
            "is_expired": parsed.is_expired,
            "cryptographic_hash": parsed.cryptographic_hash,
            "hash_matches": hash_valid,
            "verification_status": (
                "expired"
                if parsed.is_expired
                else "verified"
                if (valid_syntax and hash_valid)
                else "invalid"
            ),
        }
