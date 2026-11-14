"""SenseCAP S2108 regression coverage."""

from datetime import UTC, datetime
from unittest.mock import Mock

from lorawan_connection import DeviceDescriptor, UplinkEvent

from sensecap_lorawan import S2108


def test_real_payload_decodes_epsilon() -> None:
    descriptor = DeviceDescriptor(
        network_id="network",
        dev_eui="2cf7f1c054300198",
        name="S2108",
        application_id="application",
        profile_id=S2108.identifiers["chirpstack"][1],
        brand_id=S2108.identifiers["chirpstack"][0],
        stack="chirpstack",
    )
    device = S2108(descriptor)
    listener = Mock()
    device.add_update_listener(listener)
    payload = bytes.fromhex(
        "010610f244000001071000000000010c1000000000016d10a2030000"
        "016c1000000000f0f3"
    )
    device._receive_event(
        UplinkEvent(
            network_id="network",
            dev_eui=descriptor.dev_eui,
            received_at=datetime.now(UTC),
            data=payload,
            f_port=2,
        )
    )
    assert device.soil_temperature == 17.65
    assert device.soil_moisture == 0
    assert device.bulk_ec == 0
    assert device.pore_ec == 0
    assert device.epsilon == 0.93
    listener.assert_called_once_with()


def test_out_of_range_value_is_discarded() -> None:
    descriptor = DeviceDescriptor(
        network_id="network",
        dev_eui="2cf7f1c054300198",
        name="S2108",
        application_id="application",
        profile_id=S2108.identifiers["chirpstack"][1],
        brand_id=S2108.identifiers["chirpstack"][0],
        stack="chirpstack",
    )
    device = S2108(descriptor)
    invalid = bytes([1, 0x07, 0x10]) + (101_000).to_bytes(4, "little") + b"\x00\x00"
    device._receive_event(
        UplinkEvent(
            network_id="network",
            dev_eui=descriptor.dev_eui,
            received_at=datetime.now(UTC),
            data=invalid,
            f_port=2,
        )
    )
    assert device.soil_moisture is None
