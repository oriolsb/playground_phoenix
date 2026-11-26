"""The chat: a player talks to the players in the same location."""

from ..kata import Message
from .rules import utc_stamp
from .state import ChatMessage, GameState


class SendMessageUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str, text: str) -> None:
        state = self.game.player(player_sid)
        self.game.chat.append(
            ChatMessage(location=state.location, name=state.name, text=text, at=utc_stamp(self.game.ports.clock))
        )
        # A chat line counts as a move (observed; nobody wrote down why).
        state.moves += 1


class ReadMessagesUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str) -> list[Message]:
        state = self.game.player(player_sid)
        return [
            Message(name=message.name, text=message.text, at=message.at)
            for message in self.game.chat
            if message.location == state.location
        ]
