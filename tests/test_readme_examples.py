import asyncio

import pytest
import xdoctest

from .conftest import (
    get_device_for_fixture_protocol,
    get_fixture_info,
    patch_discovery,
)


def test_bulb_examples(mocker):
    """Use KL130 (bulb with all features) to test the doctests."""
    p = asyncio.run(get_device_for_fixture_protocol("KL130(US)_1.0_1.8.11.json", "IOT"))
    mocker.patch("kasa.iot.iotbulb.IotBulb", return_value=p)
    mocker.patch("kasa.iot.iotbulb.IotBulb.update")
    res = xdoctest.doctest_module("kasa.iot.iotbulb", "all")
    assert not res["failed"]


def test_smartdevice_examples(mocker):
    """Use HS110 for emeter examples."""
    p = asyncio.run(get_device_for_fixture_protocol("HS110(EU)_1.0_1.2.5.json", "IOT"))
    mocker.patch("kasa.iot.iotdevice.IotDevice", return_value=p)
    mocker.patch("kasa.iot.iotdevice.IotDevice.update")
    res = xdoctest.doctest_module("kasa.iot.iotdevice", "all")
    assert not res["failed"]


def test_plug_examples(mocker):
    """Test plug examples."""
    p = asyncio.run(get_device_for_fixture_protocol("HS110(EU)_1.0_1.2.5.json", "IOT"))
    # p = await get_device_for_fixture_protocol("HS110(EU)_1.0_1.2.5.json", "IOT")
    mocker.patch("kasa.iot.iotplug.IotPlug", return_value=p)
    mocker.patch("kasa.iot.iotplug.IotPlug.update")
    res = xdoctest.doctest_module("kasa.iot.iotplug", "all")
    assert not res["failed"]


def test_strip_examples(mocker):
    """Test strip examples."""
    p = asyncio.run(get_device_for_fixture_protocol("KP303(UK)_1.0_1.0.3.json", "IOT"))
    mocker.patch("kasa.iot.iotstrip.IotStrip", return_value=p)
    mocker.patch("kasa.iot.iotstrip.IotStrip.update")
    res = xdoctest.doctest_module("kasa.iot.iotstrip", "all")
    assert not res["failed"]


def test_dimmer_examples(mocker):
    """Test dimmer examples."""
    p = asyncio.run(get_device_for_fixture_protocol("HS220(US)_1.0_1.5.7.json", "IOT"))
    mocker.patch("kasa.iot.iotdimmer.IotDimmer", return_value=p)
    mocker.patch("kasa.iot.iotdimmer.IotDimmer.update")
    res = xdoctest.doctest_module("kasa.iot.iotdimmer", "all")
    assert not res["failed"]


def test_lightstrip_examples(mocker):
    """Test lightstrip examples."""
    p = asyncio.run(get_device_for_fixture_protocol("KL430(US)_1.0_1.0.10.json", "IOT"))
    mocker.patch("kasa.iot.iotlightstrip.IotLightStrip", return_value=p)
    mocker.patch("kasa.iot.iotlightstrip.IotLightStrip.update")
    res = xdoctest.doctest_module("kasa.iot.iotlightstrip", "all")
    assert not res["failed"]


def test_discovery_examples(readmes_mock):
    """Test discovery examples."""
    res = xdoctest.doctest_module("kasa.discover", "all")
    assert res["n_passed"] > 0
    assert res["n_warned"] == 0
    assert not res["failed"]


def test_deviceconfig_examples(readmes_mock):
    """Test discovery examples."""
    res = xdoctest.doctest_module("kasa.deviceconfig", "all")
    assert res["n_passed"] > 0
    assert res["n_warned"] == 0
    assert not res["failed"]


def test_device_examples(readmes_mock):
    """Test device examples."""
    res = xdoctest.doctest_module("kasa.device", "all")
    assert res["n_passed"] > 0
    assert res["n_warned"] == 0
    assert not res["failed"]


def test_light_examples(readmes_mock):
    """Test device examples."""
    res = xdoctest.doctest_module("kasa.interfaces.light", "all")
    assert res["n_passed"] > 0
    assert res["n_warned"] == 0
    assert not res["failed"]


def test_light_preset_examples(readmes_mock):
    """Test device examples."""
    res = xdoctest.doctest_module("kasa.interfaces.lightpreset", "all")
    assert res["n_passed"] > 0
    assert res["n_warned"] == 0
    assert not res["failed"]


def test_light_effect_examples(readmes_mock):
    """Test device examples."""
    res = xdoctest.doctest_module("kasa.interfaces.lighteffect", "all")
    assert res["n_passed"] > 0
    assert res["n_warned"] == 0
    assert not res["failed"]


def test_child_examples(readmes_mock):
    """Test device examples."""
    res = xdoctest.doctest_module("kasa.smart.modules.childdevice", "all")
    assert res["n_passed"] > 0
    assert res["n_warned"] == 0
    assert not res["failed"]


def test_module_examples(readmes_mock):
    """Test device examples."""
    res = xdoctest.doctest_module("kasa.module", "all")
    assert res["n_passed"] > 0
    assert res["n_warned"] == 0
    assert not res["failed"]


def test_feature_examples(readmes_mock):
    """Test device examples."""
    res = xdoctest.doctest_module("kasa.feature", "all")
    assert res["n_passed"] > 0
    assert res["n_warned"] == 0
    assert not res["failed"]


def test_tutorial_examples(readmes_mock):
    """Test discovery examples."""
    res = xdoctest.doctest_module("docs/tutorial.py", "all")
    assert res["n_passed"] > 0
    assert res["n_warned"] == 0
    assert not res["failed"]


@pytest.fixture()
async def readmes_mock(mocker):
    fixture_infos = {
        "127.0.0.1": get_fixture_info("KP303(UK)_1.0_1.0.3.json", "IOT"),  # Strip
        "127.0.0.2": get_fixture_info("HS110(EU)_1.0_1.2.5.json", "IOT"),  # Plug
        "127.0.0.3": get_fixture_info("L530E(EU)_3.0_1.1.6.json", "SMART"),  # Bulb
        "127.0.0.4": get_fixture_info("KL430(US)_1.0_1.0.10.json", "IOT"),  # Lightstrip
        "127.0.0.5": get_fixture_info("HS220(US)_1.0_1.5.7.json", "IOT"),  # Dimmer
    }
    return patch_discovery(fixture_infos, mocker)
