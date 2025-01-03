import datetime
from unittest.mock import Mock

import pytest
from voluptuous import (
    All,
    Any,
    Coerce,
    Range,
    Schema,
)

from kasa import Device, DeviceType, EmeterStatus, Module
from kasa.interfaces.energy import Energy
from kasa.iot import IotDevice, IotStrip
from kasa.iot.modules.emeter import Emeter
from kasa.smart import SmartDevice
from kasa.smart.modules import Energy as SmartEnergyModule

from .conftest import has_emeter, has_emeter_iot, no_emeter

CURRENT_CONSUMPTION_SCHEMA = Schema(
    Any(
        {
            "voltage": Any(All(float, Range(min=0, max=300)), None),
            "power": Any(Coerce(float), None),
            "total": Any(Coerce(float), None),
            "current": Any(All(float), None),
            "voltage_mv": Any(All(float, Range(min=0, max=300000)), int, None),
            "power_mw": Any(Coerce(float), None),
            "total_wh": Any(Coerce(float), None),
            "current_ma": Any(All(float), int, None),
            "slot_id": Any(Coerce(int), None),
        },
        None,
    )
)


@no_emeter
async def test_no_emeter(dev):
    assert not dev.has_emeter

    with pytest.raises(AttributeError):
        await dev.get_emeter_realtime()
    # Only iot devices support the historical stats so other
    # devices will not implement the methods below
    if isinstance(dev, IotDevice):
        with pytest.raises(AttributeError):
            await dev.get_emeter_daily()
        with pytest.raises(AttributeError):
            await dev.get_emeter_monthly()
        with pytest.raises(AttributeError):
            await dev.erase_emeter_stats()


@has_emeter
async def test_get_emeter_realtime(dev):
    if isinstance(dev, SmartDevice):
        mod = SmartEnergyModule(dev, str(Module.Energy))
        if not await mod._check_supported():
            pytest.skip(f"Energy module not supported for {dev}.")

    emeter = dev.modules[Module.Energy]

    current_emeter = await emeter.get_status()
    CURRENT_CONSUMPTION_SCHEMA(current_emeter)


@has_emeter_iot
@pytest.mark.requires_dummy()
async def test_get_emeter_daily(dev):
    emeter = dev.modules[Module.Energy]

    assert await emeter.get_daily_stats(year=1900, month=1) == {}

    d = await emeter.get_daily_stats()
    assert len(d) > 0

    k, v = d.popitem()
    assert isinstance(k, int)
    assert isinstance(v, float)

    # Test kwh (energy, energy_wh)
    d = await emeter.get_daily_stats(kwh=False)
    k2, v2 = d.popitem()
    assert v * 1000 == v2


@has_emeter_iot
@pytest.mark.requires_dummy()
async def test_get_emeter_monthly(dev):
    emeter = dev.modules[Module.Energy]

    assert await emeter.get_monthly_stats(year=1900) == {}

    d = await emeter.get_monthly_stats()
    assert len(d) > 0

    k, v = d.popitem()
    assert isinstance(k, int)
    assert isinstance(v, float)

    # Test kwh (energy, energy_wh)
    d = await emeter.get_monthly_stats(kwh=False)
    k2, v2 = d.popitem()
    assert v * 1000 == v2


@has_emeter_iot
async def test_emeter_status(dev):
    emeter = dev.modules[Module.Energy]

    d = await emeter.get_status()

    with pytest.raises(KeyError):
        assert d["foo"]

    assert d["power_mw"] == d["power"] * 1000
    # bulbs have only power according to tplink simulator.
    if (
        dev.device_type is not DeviceType.Bulb
        and dev.device_type is not DeviceType.LightStrip
    ):
        assert d["voltage_mv"] == d["voltage"] * 1000

        assert d["current_ma"] == d["current"] * 1000
        assert d["total_wh"] == d["total"] * 1000


@pytest.mark.skip("not clearing your stats..")
@has_emeter
async def test_erase_emeter_stats(dev):
    emeter = dev.modules[Module.Energy]

    await emeter.erase_emeter()


@has_emeter_iot
async def test_current_consumption(dev):
    emeter = dev.modules[Module.Energy]
    x = emeter.current_consumption
    assert isinstance(x, float)
    assert x >= 0.0


async def test_emeterstatus_missing_current():
    """KL125 does not report 'current' for emeter."""
    regular = EmeterStatus(
        {"err_code": 0, "power_mw": 0, "total_wh": 13, "current_ma": 123}
    )
    assert regular["current"] == 0.123

    with pytest.raises(KeyError):
        regular["invalid_key"]

    missing_current = EmeterStatus({"err_code": 0, "power_mw": 0, "total_wh": 13})
    assert missing_current["current"] is None


async def test_emeter_daily():
    """Test fetching the emeter for today.

    This test uses inline data since the fixtures
    will not have data for the current day.
    """
    emeter_data = {
        "get_daystat": {
            "day_list": [{"day": 1, "energy_wh": 8, "month": 1, "year": 2023}],
            "err_code": 0,
        }
    }

    class MockEmeter(Emeter):
        @property
        def data(self):
            return emeter_data

    emeter = MockEmeter(Mock(), "emeter")
    now = datetime.datetime.now()
    emeter_data["get_daystat"]["day_list"].append(
        {"day": now.day, "energy_wh": 500, "month": now.month, "year": now.year}
    )
    assert emeter.consumption_today == 0.500


@has_emeter
async def test_supported(dev: Device):
    if isinstance(dev, SmartDevice):
        mod = SmartEnergyModule(dev, str(Module.Energy))
        if not await mod._check_supported():
            pytest.skip(f"Energy module not supported for {dev}.")
    energy_module = dev.modules.get(Module.Energy)
    assert energy_module
    if isinstance(dev, IotDevice):
        info = (
            dev._last_update
            if not isinstance(dev, IotStrip)
            else dev.children[0].internal_state
        )
        emeter = info[energy_module._module]["get_realtime"]
        has_total = "total" in emeter or "total_wh" in emeter
        has_voltage_current = "voltage" in emeter or "voltage_mv" in emeter
        assert (
            energy_module.supports(Energy.ModuleFeature.CONSUMPTION_TOTAL) is has_total
        )
        assert (
            energy_module.supports(Energy.ModuleFeature.VOLTAGE_CURRENT)
            is has_voltage_current
        )
        assert energy_module.supports(Energy.ModuleFeature.PERIODIC_STATS) is True
    else:
        assert energy_module.supports(Energy.ModuleFeature.CONSUMPTION_TOTAL) is False
        assert energy_module.supports(Energy.ModuleFeature.VOLTAGE_CURRENT) is False
        assert energy_module.supports(Energy.ModuleFeature.PERIODIC_STATS) is False
