"""The chat of a location (CHAT-*)."""

from datetime import datetime, timezone

from .. import kata
from .game import Game
from .state import ChatMessage


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SendMessageUseCase:
    def __init__(self, game: Game) -> None:
        self.game = game

    def execute(self, player_sid: str, text: str) -> str:
        state = self.game.player(player_sid)
        self.game.chat.append(
            ChatMessage(location=state.location, name=state.name, text=text, at=now_iso())
        )
        state.moves += 1
        return "SENT."


class ReadMessagesUseCase:
    def __init__(self, game: Game) -> None:
        self.game = game

    def execute(self, player_sid: str) -> list[kata.ChatMessage]:
        state = self.game.player(player_sid)
        return [
            kata.ChatMessage(name=message.name, text=message.text, at=message.at)
            for message in self.game.chat
            if message.location == state.location
        ]
