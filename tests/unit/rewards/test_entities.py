import pytest
from rewards.core.domain.entities import UserPoints


def test_user_points_calculate():
    assert UserPoints.calculate(1000) == 1