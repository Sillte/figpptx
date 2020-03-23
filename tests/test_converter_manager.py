import matplotlib.pyplot as plt
from PIL import Image
from figpptx.converter_manager import ConverterManager
from unittest.mock import MagicMock
import matplotlib

import pytest


class _MockArtist(matplotlib.artist.Artist):
    pass


@ConverterManager.register(_MockArtist)
def _for_mock_artist(slide_editor, artist):
    assert isinstance(artist, _MockArtist)
    slide_editor.called = True
    artist.called = True


def test_fetch():
    roster = ConverterManager.roster
    assert isinstance(roster, dict)

    artist = _MockArtist()
    slide_editor = MagicMock()
    func = ConverterManager.fetch(artist)
    func(slide_editor, artist)
    assert artist.called
    assert slide_editor.called


def test_register_exception():
    def func(editor, artist):
        pass

    with pytest.raises(ValueError):
        ConverterManager.register(int)(func)


if __name__ == "__main__":
    pytest.main([__file__, "--capture=no"])
