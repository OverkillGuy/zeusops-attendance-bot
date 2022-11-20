"""Basic tests of zeusops_attendance_bot CLI"""
import os

import pytest

from zeusops_attendance_bot.cli import cli

API_AUTH_TOK = "not-a-real-pass123deadb0b"


@pytest.skip("Borked CLI test")
def test_cli_set_token_envvar(mocker, capsys):
    """Check we can set token via envvar"""
    MOCKED_API_RESPONSE = {"mocked": True}
    # Given a patched run function
    mocked_run_call = mocker.patch(
        "zeusops_attendance_bot.cli.run", return_value=MOCKED_API_RESPONSE
    )
    # And a DISCORD_API_TOKEN envvar
    mocker.patch.dict(os.environ, {"DISCORD_API_TOKEN": API_AUTH_TOK})
    # When I call the CLI
    cli([])
    # Then the mock runfunc was hit
    assert mocked_run_call.called, "Mock API should have been hit"
    # And the mocked response is printed
    assert "mocked" in capsys.readouterr().out, "Didn't hit the mocked runfunc"
    # And no error message
    assert not capsys.readouterr().err, "Shouldn't see any error"
