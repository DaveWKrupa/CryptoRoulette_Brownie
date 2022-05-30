from brownie import exceptions, CryptoRoulette, network
from scripts.deploy import deploy
from scripts.helper_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from web3 import Web3
from datetime import datetime

# 0xB439Bf7bC29Ce76903CF2a4B547A87d8dfcbe605 rinkeby


def test_deploy():
    cryptoRoulette = deploy()
    print(cryptoRoulette)


def test_dealer_start_game():
    # everything should work

    account = get_account(configkey="private_key_player1")

    cryptoRoulette = CryptoRoulette[-1]  # get the latest published
    print(cryptoRoulette)

    newGameKey = (
        str(account)[:5]
        + "..."
        + str(account)[len(str(account)) - 5 : len(str(account))]
        + "_"
        + str(datetime.utcnow())
    )

    print("newGameKey")
    print(newGameKey)

    ante = Web3.toWei(0.001, "ether")
    start_game_tx = cryptoRoulette.startNewGame(
        ante, newGameKey, {"from": account, "value": ante}
    )
    games = cryptoRoulette.getGames(True)
    print("games")
    print(games)
    game_added = newGameKey in games
    assert (game_added, "Game not added")
    dealerGameStatus = cryptoRoulette.getGameStatus(newGameKey)
    print(dealerGameStatus)
    assert (
        dealerGameStatus == "Waiting for players",
        "Game status incorrect on start.",
    )
    if game_added:
        print("game added")

        newgamedealer = start_game_tx.events["newGameStarted"]["dealer"]
        newgamegameKey = start_game_tx.events["newGameStarted"]["gameKey"]
        newgametimeStamp = start_game_tx.events["newGameStarted"]["timeStamp"]
        newgameante = start_game_tx.events["newGameStarted"]["ante"]
        print("new game event / change status event")
        newstatus = start_game_tx.events["gameStatusChanged"]["newStatus"]
        print(newgamedealer, newgamegameKey, newgametimeStamp, newgameante, newstatus)


def test_get_games():
    cryptoRoulette = CryptoRoulette[-1]  # get the latest published
    games = cryptoRoulette.getGames(True)
    print("games")
    print(games)


def test_get_game_info():
    cryptoRoulette = CryptoRoulette[-1]
    newGameKey = "0x4A2...22e85_2022-05-30 03:04:58.517056"

    (
        dealer,
        ante,
        gameStatus,
        potAmount,
        playerCount,
        currentRound,
    ) = cryptoRoulette.getGameInfo(newGameKey)

    print("gameinfo")
    print(
        dealer,
        ante,
        gameStatus,
        potAmount,
        playerCount,
        currentRound,
    )

    (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
    print("address and stack")
    print(playerAddresses)
    print(playerStacks)
