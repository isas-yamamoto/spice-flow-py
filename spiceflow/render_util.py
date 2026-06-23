"""Pure helpers for render compositing (no pyrender import)."""


def bg_color_rgba(bg_color):
    """Return RGBA tuple without mutating the caller's sequence."""
    if bg_color is None:
        return (0.0, 0.0, 0.0, 1.0)

    values = list(bg_color)
    if len(values) == 3:
        values.append(1.0)
    if len(values) < 4:
        return (0.0, 0.0, 0.0, 1.0)
    return tuple(float(v) for v in values[:4])
