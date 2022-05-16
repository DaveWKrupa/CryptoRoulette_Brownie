from brownie import exceptions, CryptoRoulette
from scripts.deploy import deploy
from scripts.helper_scripts import get_account
from web3 import Web3


def test_deploy():
    cryptoRoulette = deploy()
    print(cryptoRoulette)


def test_dealer_start_end_game_success():
    # everything should work

    try:
        cryptoRoulette = CryptoRoulette[-1]
    except IndexError:
        account = get_account()
        cryptoRoulette = deploy()

    newGameKey = "mynewgamekey"  # needs to be changed each run on same contract
    ante = Web3.toWei(0.01, "ether")
    cryptoRoulette.startNewGame(ante, newGameKey, {"from": account, "value": ante})
    games = cryptoRoulette.getGames(True)
    print(games)
    game_added = newGameKey in games
    assert (game_added, "Game not added")
    dealerGameStatus = cryptoRoulette.getGameStatus(newGameKey)
    print("dealerGameStatus")
    assert (
        dealerGameStatus == "Waiting for players",
        "Game status incorrect on start.",
    )
    if game_added:
        cryptoRoulette.endGame({"from": account})
        games = cryptoRoulette.getGames(True)
        print("games")
        print(games)
        assert (games == tuple(), "Games array still has active game.")
        dealerGameStatus = cryptoRoulette.getGameStatus(newGameKey)
        print(dealerGameStatus)
        assert (dealerGameStatus == "Game ended", "Game status incorrect on end.")
        (players, stacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print(players)
        print(stacks)


def test_dealer_start_two_games():
    # starting the first game should work
    # starting the second game should not

    try:
        cryptoRoulette = CryptoRoulette[-1]
    except IndexError:
        account = get_account()
        cryptoRoulette = deploy()

    newGameKey = "mynewgamekey"  # needs to be changed each run on same contract
    ante = Web3.toWei(0.01, "ether")
    cryptoRoulette.startNewGame(ante, newGameKey, {"from": account, "value": ante})
    games = cryptoRoulette.getGames(True)
    print(games)
    game_added = newGameKey in games
    dealerGameStatus = cryptoRoulette.getGameStatus(newGameKey)
    print("dealerGameStatus")
    print(dealerGameStatus)
    if game_added:

        try:
            cryptoRoulette.startNewGame(
                ante, newGameKey, {"from": account, "value": ante}
            )
            assert (False, "Game in progress error not thrown.")
        except exceptions.VirtualMachineError as e:
            print(e)
            assert (
                e == "revert: You already have a game in progress.",
                "Incorrect error.",
            )