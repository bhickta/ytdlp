from ytdlp_subs.infrastructure.command_executor import CommandExecutor
from ytdlp_subs.infrastructure.repositories.video_repository import YtDlpVideoRepository


def make_repository() -> YtDlpVideoRepository:
    return YtDlpVideoRepository(command_executor=CommandExecutor())


def test_watch_url_with_list_is_treated_as_playlist() -> None:
    repo = make_repository()
    url = "https://www.youtube.com/watch?v=bNTZSqev3c8&list=PLpKGxj880QG2XsEScxuDhPCLJ7NbZ58J1"

    command = repo._build_channel_command(url)

    assert not repo.is_video_url(url)
    assert command[-4:] == ["--flat-playlist", "--print", "id", url]


def test_short_url_with_list_is_treated_as_playlist() -> None:
    repo = make_repository()
    url = "https://youtu.be/OXh5ok4GU-4?list=PLg5vXp1Sasokg-1VUqYZhoIgpPZ1dDD8y"

    command = repo._build_channel_command(url)

    assert not repo.is_video_url(url)
    assert command[-4:] == ["--flat-playlist", "--print", "id", url]


def test_plain_watch_url_is_treated_as_single_video() -> None:
    repo = make_repository()
    url = "https://www.youtube.com/watch?v=bNTZSqev3c8"

    command = repo._build_channel_command(url)

    assert repo.is_video_url(url)
    assert command[-4:] == ["--no-playlist", "--print", "id", url]


def test_plain_short_url_is_treated_as_single_video() -> None:
    repo = make_repository()
    url = "https://youtu.be/bNTZSqev3c8"

    command = repo._build_channel_command(url)

    assert repo.is_video_url(url)
    assert command[-4:] == ["--no-playlist", "--print", "id", url]
