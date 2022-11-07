"""Basic tests of zeusops_attendance_bot CLI"""
import os

from zeusops_attendance_bot.cli import cli

API_AUTH_TOK = "not-a-real-pass123deadb0b"


def test_cli_set_token_envvar(mocker, capsys):
    """Check we can set token via envvar"""
    MOCKED_API_RESPONSE = {"mocked": True}
    # Given a patched API request function
    mocked_api_call = mocker.patch(
        "zeusops_attendance_bot.cli.get_from_api", return_value=MOCKED_API_RESPONSE
    )
    # And a DISCORD_API_TOKEN envvar
    mocker.patch.dict(os.environ, {"DISCORD_API_TOKEN": API_AUTH_TOK})
    # When I call the API-fetching CLI
    cli([])
    # Then the mock API was hit
    assert mocked_api_call.called, "Mock API should have been hit"
    # And the mocked response is printed
    assert "mocked" in capsys.readouterr().out, "Didn't hit the mocked API"
    # And no error message
    assert not capsys.readouterr().err, "Shouldn't see any error"


def test_cli_set_token_file(mocker, capsys, tmp_path):
    """Check we can set token via envvar"""
    MOCKED_API_RESPONSE = {"mocked": True}
    # Given a patched API request function
    mocked_api_call = mocker.patch(
        "zeusops_attendance_bot.cli.get_from_api", return_value=MOCKED_API_RESPONSE
    )
    # And a DISCORD_API_TOKEN as file
    auth_tok_filepath = tmp_path / ".auth"
    with open(auth_tok_filepath, "w") as token_fd:
        token_fd.write(API_AUTH_TOK)
    # When I call the API-fetching CLI
    cli(["--token-file", str(auth_tok_filepath)])
    # Then the mock API was hit
    assert mocked_api_call.called, "Mock API should have been hit"
    # And the mocked response is printed
    assert "mocked" in capsys.readouterr().out, "Didn't hit the mocked API"
    # And no error message
    assert not capsys.readouterr().err, "Shouldn't see any error"
