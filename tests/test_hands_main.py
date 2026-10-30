from oak_hands.main import parse_arguments


def test_live_feed_is_off_by_default():
    assert not parse_arguments([]).live_feed


def test_live_feed_flag_turns_it_on():
    assert parse_arguments(["--live-feed"]).live_feed
