from brownie import exceptions, CryptoRoulette, network
from scripts.deploy import deploy
from scripts.helper_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from web3 import Web3
import pytest


def test_deploy():
    cryptoRoulette = deploy()
    print(cryptoRoulette)


def test_player_get_fee():
    # fee is 10 times the ante
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        account = get_account(index=0)
    else:
        account = get_account(configkey="private_key_player1")

    cryptoRoulette = deploy()

    newGameKey = "mynewgamekey"  # needs to be changed each run on same contract
    ante = Web3.toWei(0.01, "ether")
    cryptoRoulette.startNewGame(ante, newGameKey, {"from": account, "value": ante})
    games = cryptoRoulette.getGames(True)
    print(games)
    game_added = newGameKey in games
    assert game_added, "Game not added"
    dealerGameStatus = cryptoRoulette.getGameStatus(newGameKey)
    print(dealerGameStatus)
    assert dealerGameStatus == "Waiting for players", "Game status incorrect on start."

    if game_added:
        fee = cryptoRoulette.getPlayerFee(newGameKey)
        print(fee)
        assert fee == ante * 10, "Fee does not equal ante times ten."
    else:
        assert False, "Game not added."


def test_player_join_game():
    #   dealer is going to join game after starting it
    # everything should work

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        account = get_account(index=0)
    else:
        account = get_account(configkey="private_key_player1")

    cryptoRoulette = deploy()

    newGameKey = "mynewgamekey"  # needs to be changed each run on same contract
    ante = Web3.toWei(0.01, "ether")
    cryptoRoulette.startNewGame(ante, newGameKey, {"from": account, "value": ante})
    games = cryptoRoulette.getGames(True)
    print(games)
    game_added = newGameKey in games
    # assert (game_added, "Game not added")
    dealerGameStatus = cryptoRoulette.getGameStatus(newGameKey)
    print(dealerGameStatus)
    # assert (
    #     dealerGameStatus == "Waiting for players",
    #     "Game status incorrect on start.",
    # )
    if game_added:
        gameKeys = cryptoRoulette.getDealerGameKeys(account)
        print(gameKeys)

        print("game added")
        fee = cryptoRoulette.getPlayerFee(newGameKey)
        print(fee)
        cryptoRoulette.joinGame(newGameKey, {"from": account, "value": fee})

        (
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        ) = cryptoRoulette.getGameInfo(newGameKey)

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
        print(playerAddresses[0])
        print(playerStacks[0])
        assert playerAddresses[0] == account, "Player not added"
        assert playerStacks[0] == fee, "Fee not added"


def test_all_players_join_game():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return  # only use this in local blockchain environment
    #   dealer is going to join game after starting it
    # then 5 other players will join the game
    # a seventh player will try to join the game but will not be able to
    dealerAcct1 = get_account(index=0)
    playerAcct1 = dealerAcct1  # dealer is also player 1
    playerAcct2 = get_account(index=1)
    playerAcct3 = get_account(index=2)
    playerAcct4 = get_account(index=3)
    playerAcct5 = get_account(index=4)
    playerAcct6 = get_account(index=5)
    playerAcct7 = get_account(index=6)

    cryptoRoulette = deploy()

    newGameKey = "mynewgamekey"  # needs to be changed each run on same contract
    ante = Web3.toWei(0.01, "ether")
    cryptoRoulette.startNewGame(ante, newGameKey, {"from": dealerAcct1, "value": ante})
    games = cryptoRoulette.getGames(True)
    print(games)
    game_added = newGameKey in games
    assert game_added, "Game not added"
    dealerGameStatus = cryptoRoulette.getGameStatus(newGameKey)
    print(dealerGameStatus)
    assert dealerGameStatus == "Waiting for players", "Game status incorrect on start."

    if game_added:
        gameKeys = cryptoRoulette.getDealerGameKeys(dealerAcct1)
        print(gameKeys)

        print("game added")
        fee = cryptoRoulette.getPlayerFee(newGameKey)
        print(fee)
        cryptoRoulette.joinGame(newGameKey, {"from": playerAcct1, "value": fee})

        (
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        ) = cryptoRoulette.getGameInfo(newGameKey)

        print(
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        )
        assert playerCount == 1, "Incorrect player count, should be 1"

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack")
        print(playerAddresses[0])
        print(playerStacks[0])
        assert playerAddresses[0] == playerAcct1, "Player not added"
        assert playerStacks[0] == fee, "Fee not added"

        cryptoRoulette.joinGame(newGameKey, {"from": playerAcct2, "value": fee})

        (
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        ) = cryptoRoulette.getGameInfo(newGameKey)

        print(
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        )
        assert playerCount == 2, "Incorrect player count, should be 2"
        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack")
        print(playerAddresses[1])
        print(playerStacks[1])
        assert playerAddresses[1] == playerAcct2, "Player not added"
        assert playerStacks[1] == fee, "Fee not added"

        cryptoRoulette.joinGame(newGameKey, {"from": playerAcct3, "value": fee})

        (
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        ) = cryptoRoulette.getGameInfo(newGameKey)

        print(
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        )
        assert playerCount == 3, "Incorrect player count, should be 3"
        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack")
        print(playerAddresses[2])
        print(playerStacks[2])
        assert playerAddresses[2] == playerAcct3, "Player not added"
        assert playerStacks[2] == fee, "Fee not added"

        cryptoRoulette.joinGame(newGameKey, {"from": playerAcct4, "value": fee})

        (
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        ) = cryptoRoulette.getGameInfo(newGameKey)

        print(
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        )
        assert playerCount == 4, "Incorrect player count, should be 4"
        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack")
        print(playerAddresses[3])
        print(playerStacks[3])
        assert playerAddresses[3] == playerAcct4, "Player not added"
        assert playerStacks[3] == fee, "Fee not added"

        cryptoRoulette.joinGame(newGameKey, {"from": playerAcct5, "value": fee})

        (
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        ) = cryptoRoulette.getGameInfo(newGameKey)

        print(
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        )
        assert playerCount == 5, "Incorrect player count, should be 5"
        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack")
        print(playerAddresses[4])
        print(playerStacks[4])
        assert playerAddresses[4] == playerAcct5, "Player not added"
        assert playerStacks[4] == fee, "Fee not added"

        cryptoRoulette.joinGame(newGameKey, {"from": playerAcct6, "value": fee})

        (
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        ) = cryptoRoulette.getGameInfo(newGameKey)

        print(
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        )
        assert playerCount == 6, "Incorrect player count, should be 6"
        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack")
        print(playerAddresses[5])
        print(playerStacks[5])
        assert playerAddresses[5] == playerAcct6, "Player not added"
        assert playerStacks[5] == fee, "Fee not added"

        # all players have been added
        # the next player should not be allowed to join
        with pytest.raises(exceptions.VirtualMachineError):
            cryptoRoulette.joinGame(newGameKey, {"from": playerAcct7, "value": fee})

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("Final players")
        print(playerAddresses)
        print(playerStacks)
