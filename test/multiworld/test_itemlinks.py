import unittest
from unittest import TestCase

from BaseClasses import MultiWorld
from test.general import setup_multiworld

class ItemLinkTestBase(TestCase):
    multiworld: MultiWorld


class TestItemLinkDefaults(ItemLinkTestBase):
    def test_defaults(self) -> None:
        """Tests that the ItemLink Defaults are set correctly."""
        # Prepare

        # Act

        # Assert