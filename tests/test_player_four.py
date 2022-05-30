from brownie import CryptoRoulette
from scripts.helper_scripts import get_account


def test_player_four_join_game():
    #   dealer is going to join game after starting it
    # everything should work

    account = get_account(configkey="private_key_player4")

    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)

    newGameKey = "0x4A2...22e85_2022-05-30 03:04:58.517056"  # needs to be changed each run on same contract
    fee = cryptoRoulette.getPlayerFee(newGameKey)
    print(fee)

    joinGameTransaction = cryptoRoulette.joinGame(
        newGameKey, {"from": account, "value": fee}
    )
    print(joinGameTransaction)

    player = joinGameTransaction.events["playerJoined"]["player"]
    gameKey = joinGameTransaction.events["playerJoined"]["gameKey"]
    timestamp = joinGameTransaction.events["playerJoined"]["timeStamp"]
    print("join event")
    print(player, gameKey, timestamp)

    # (
    #     dealer,
    #     ante,
    #     gameStatus,
    #     potAmount,
    #     playerCount,
    #     currentRound,
    # ) = cryptoRoulette.getGameInfo(newGameKey)

    # print("gameinfo")
    # print(
    #     dealer,
    #     ante,
    #     gameStatus,
    #     potAmount,
    #     playerCount,
    #     currentRound,
    # )

    # (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
    # print("address and stack")
    # print(playerAddresses)
    # print(playerStacks)
