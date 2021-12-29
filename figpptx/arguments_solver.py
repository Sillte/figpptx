"""Arguments Solver.

For functions ``__init__.py``, ``ArgumentSolver`` provides
interpretation of arguments.

"""
from figpptx import pptx_misc
from collections.abc import Sequence


class PositionSolver:
    """Based on ``Slide`` and size of ``target``,
    calculate the appropriate ``left`` and ``top`` position.

    """

    target_keys = {"left", "top", "pos"}

    def __init__(self, slide, size):
        self.slide = slide
        self.target_width, self.target_height = size
        self.slide_width, self.slide_height = pptx_misc.get_slide_size(self.slide)

        self._left = None
        self._top = None
        self._pos = None

    def configure(self, kwargs):
        """Set the intended attributes with the given
            ``kwargs``.

        Note
        ----
        Case Insensitive. This is following to convention of VBA.
        """

        for key in kwargs:
            if key.lower() in self.target_keys:
                setattr(self, f"_{key.lower()}", kwargs[key])

        if self._left is None or self._top is None:
            """Direct specification of ``left`` and ``top``
            is the highest priority.
            """
            left, top = self._solve()
            if self._left is None:
                self._left = left
            if self._top is None:
                self._top = top

        assert self._left is not None
        assert self._top is not None
        return (self.left, self.top)

    def _solve(self):
        left = None
        top = None
        if self._pos is not None:
            left, top = self._solve_pos(self._pos)
        if left is None:
            left = self._default_left()
        if top is None:
            top = self._default_top()
        return left, top

    def _solve_pos(self, pos):
        # For the case ``pos`` represents (left, top).
        if isinstance(pos, Sequence):
            assert len(pos) == 2
            left, top = self._pos
            return left, top
        elif callable(pos):
            left, top = pos(self.slide, (self.target_width, self.target_height))
            return left, top
        raise ValueError("Invalid pos is given.", pos)

    def _default_left(self):
        if self.target_width < self.slide_width:
            return (self.slide_width - self.target_width) / 2
        else:
            return 0

    def _default_top(self):
        if self.target_height < self.slide_height:
            return (self.slide_height - self.target_height) / 2
        else:
            return 0

    @property
    def left(self):
        assert self._left is not None
        return self._left

    @property
    def top(self):
        assert self._top is not None
        return self._top
