from matter_bundle import decide_delivery_split


def test_decide_delivery_split():
    assert decide_delivery_split(1) is False
    assert decide_delivery_split(2) is True
    assert decide_delivery_split(5) is True
