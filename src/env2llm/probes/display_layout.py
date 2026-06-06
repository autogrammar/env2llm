"""Shared helpers for mapping global desktop coordinates to displays."""

from __future__ import annotations

from env2llm.ir import DesktopDisplayIR, DesktopPointerIR


def resolve_pointer_display(
    pointer: DesktopPointerIR,
    displays: list[DesktopDisplayIR],
) -> DesktopPointerIR:
    """Attach display-local coordinates when *pointer* lies inside a known display."""
    if not displays:
        return pointer

    for display in displays:
        if (
            display.left <= pointer.x < display.left + display.width
            and display.top <= pointer.y < display.top + display.height
        ):
            return pointer.model_copy(
                update={
                    "display_id": display.id,
                    "display_output": display.output,
                    "display_x": pointer.x - display.left,
                    "display_y": pointer.y - display.top,
                },
            )
    return pointer
