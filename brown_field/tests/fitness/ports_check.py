"""ARCH-2: each use case satisfies its port. Type-checked by mypy, never imported.

`test_structure.py` runs mypy on this file. A use case that drifts from its
port in `kata.py` gives a type error here. The function is never called: the
checker reads it, so building the game touches no file.
"""

from brown_field import kata
from brown_field.game import (
    InMemoryGame,
    InspectBagUseCase,
    InspectItemUseCase,
    LegacyPickupUseCase,
    ListPlayersUseCase,
    LoginUseCase,
    LookAroundUseCase,
    LookInDirectionUseCase,
    MoveUseCase,
    QuitGameUseCase,
    ReadMessagesUseCase,
    RegisterAccountUseCase,
    RegisterPlayerUseCase,
    SaveGameUseCase,
    SendMessageUseCase,
    ShowLeaderboardUseCase,
    UseItemUseCase,
)


def each_use_case_fits_its_port(game: InMemoryGame) -> None:
    register_player: kata.RegisterPlayer = RegisterPlayerUseCase(game)
    list_players: kata.ListPlayers = ListPlayersUseCase(game)
    quit_game: kata.QuitGame = QuitGameUseCase(game)
    inspect_item: kata.InspectItem = InspectItemUseCase(game)
    inspect_bag: kata.InspectBag = InspectBagUseCase(game)
    use_item: kata.UseItem = UseItemUseCase(game)
    look_around: kata.LookAround = LookAroundUseCase(game)
    look_in_direction: kata.LookInDirection = LookInDirectionUseCase(game)
    move: kata.Move = MoveUseCase(game)
    save_game: kata.SaveGame = SaveGameUseCase(game)
    # Decision 0015 (ENTRY-3).
    send_message: kata.SendMessage = SendMessageUseCase(game)
    read_messages: kata.ReadMessages = ReadMessagesUseCase(game)
    show_leaderboard: kata.ShowLeaderboard = ShowLeaderboardUseCase(game)
    register_account: kata.RegisterAccount = RegisterAccountUseCase(game)
    login: kata.Login = LoginUseCase(game)
    legacy_pickup: kata.LegacyPickup = LegacyPickupUseCase(game)
