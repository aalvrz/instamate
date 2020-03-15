import pytest

from pygram.workspace import UserWorkspace


@pytest.fixture
def workspace(tmpdir, monkeypatch):
    monkeypatch.setattr('pygram.workspace.DEFAULT_WORKSPACES_PATH', tmpdir)
    workspace = UserWorkspace('wololo23')

    return workspace


class TestWorkspace:
    def test_creation_on_instantiation(self, workspace):
        assert workspace.exists

    def test_add_to_and_get_follow_history(self, workspace):
        u1, u2, u3 = 'scubzer21', 'moron984', 'supabitch66'
        workspace.add_user_to_follow_history(u1)
        workspace.add_user_to_follow_history(u2)
        workspace.add_user_to_follow_history(u3)
        workspace.add_user_to_follow_history('yukop')

        follow_history = workspace.get_follow_history()

        assert len(follow_history) == 4
        assert {u1, u2, u3} <= follow_history
