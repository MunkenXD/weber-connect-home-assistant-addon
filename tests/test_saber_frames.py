from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "weber_connect_ble" / "app"
sys.path.insert(0, str(APP))

import saber_frames as frames  # noqa: E402


def tlv(tag: int, value: bytes) -> bytes:
    return bytes([tag, len(value)]) + value


class ProbeSessionStatusTlvTests(unittest.TestCase):
    def test_zero_values_are_not_overridden_by_legacy_fallback(self):
        # Tags 19/16/17/18 are the "new" fields; 4/7/11 are legacy fallbacks
        # only meant to apply when the new field is absent. A real 0 in the
        # new field (a valid probe type, plan id, step id, or prompt id)
        # must survive rather than being replaced by the legacy byte.
        payload = (
            tlv(1, bytes([0]))  # slot_index
            + tlv(19, bytes([0]))  # probe_type (new): 0 = UNKNOWN, a real value
            + tlv(4, bytes([2]))  # legacy fallback byte; must be ignored here
            + tlv(16, (0).to_bytes(4, "little"))  # plan_id (new): 0
            + tlv(17, (0).to_bytes(2, "little"))  # step_id (new): 0
            + tlv(7, bytes([9]))  # legacy fallback byte; must be ignored here
            + tlv(18, (0).to_bytes(2, "little"))  # prompt_id (new): 0
            + tlv(11, bytes([5]))  # legacy fallback byte; must be ignored here
        )

        row = frames.parse_probe_session_status_tlv(payload)

        self.assertEqual(row["probe_type_value"], 0)
        self.assertEqual(row["probe_type"], "UNKNOWN")
        self.assertEqual(row["plan_id"], 0)
        self.assertEqual(row["step_id"], 0)
        self.assertEqual(row["prompt_id"], 0)

    def test_legacy_fallback_still_applies_when_new_field_absent(self):
        payload = (
            tlv(1, bytes([0]))
            + tlv(4, bytes([2]))
            + tlv(7, bytes([9]))
            + tlv(11, bytes([5]))
        )

        row = frames.parse_probe_session_status_tlv(payload)

        self.assertEqual(row["probe_type_value"], 2)
        self.assertEqual(row["step_id"], 9)
        self.assertEqual(row["prompt_id"], 5)


if __name__ == "__main__":
    unittest.main()
