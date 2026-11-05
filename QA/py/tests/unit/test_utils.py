import pytest

from appli.utils import (
    format_date_time,
    ScaleForDisplay,
    ntcv,
    DecodeEqualList,
    EncodeEqualList,
)
from appli.back_config import bytes_to_human_readable


def test_format_date_time_formats_known_columns():
    rec = {"d": "2020-09-17T13:15:37.441179", "t": "13:15:37", "other": "2020-09-17T13:15:37"}
    format_date_time(rec, date_cols=("d",), time_cols=("t",))
    assert rec == {"d": "2020-09-17 13:15", "t": "13:15", "other": "2020-09-17T13:15:37"}


@pytest.mark.parametrize("bad", [None, "2020-09-17", "2020/09/17 13:15:37.0"])
def test_format_date_time_leaves_unexpected_values(bad):
    rec = {"d": bad}
    format_date_time(rec, date_cols=("d", "missing"))
    assert rec == {"d": bad}


@pytest.mark.parametrize(
    "val, expected",
    [(1.23456, "1.23"), (-99.999, "-100.00"), (123.6, "124"), (None, ""), ("txt", "txt"), (12, "12")],
)
def test_scale_for_display(val, expected):
    assert ScaleForDisplay(val) == expected


def test_ntcv():
    assert ntcv(None) == ""
    assert ntcv("a") == "a"


def test_decode_equal_list_lowercases_and_skips_bad_lines():
    txt = "Key1 = Value1\nno_equal_here\nk2=a=b\n"
    assert DecodeEqualList(txt) == {"key1": "value1", "k2": "a=b"}
    assert DecodeEqualList(None) == {}


def test_encode_decode_round_trip():
    data = {"b": "2", "a": "1"}
    txt = EncodeEqualList(data)
    assert txt == "a=1\nb=2"
    assert DecodeEqualList(txt) == data


@pytest.mark.parametrize(
    "num, expected",
    [(0, "0.0B"), (1023, "1023.0B"), (1024, "1.0KB"), (681574400, "650.0MB"), (1024**8 * 3, "3.0YiB")],
)
def test_bytes_to_human_readable(num, expected):
    assert bytes_to_human_readable(num) == expected


def test_xss_escape_and_helpers():
    from appli import XSSEscape, ntcv as appli_ntcv

    assert XSSEscape('<a href="x">') == "&lt;a href=&quot;x&quot;&gt;"
    assert appli_ntcv(None) == ""
