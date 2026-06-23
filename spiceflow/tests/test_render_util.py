from spiceflow.render_util import bg_color_rgba


def test_bg_color_rgba_default():
    assert bg_color_rgba(None) == (0.0, 0.0, 0.0, 1.0)


def test_bg_color_rgba_does_not_mutate_caller():
    original = [0.1, 0.2, 0.3]
    expected = list(original)
    rgba = bg_color_rgba(original)
    assert original == expected
    assert rgba == (0.1, 0.2, 0.3, 1.0)


def test_bg_color_rgba_accepts_rgba():
    assert bg_color_rgba((0.0, 0.0, 0.0, 0.5)) == (0.0, 0.0, 0.0, 0.5)
