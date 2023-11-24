import pytest

from pygram.workspace import UserWorkspace


@pytest.fixture
def workspace(tmpdir, monkeypatch):
    monkeypatch.setattr("pygram.workspace.DEFAULT_WORKSPACES_PATH", tmpdir)
    workspace = UserWorkspace("wololo23")

    return workspace


class TestWorkspace:
    def test_creation_on_instantiation(self, workspace):
        assert workspace.exists
