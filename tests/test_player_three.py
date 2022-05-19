from brownie import exceptions, CryptoRoulette
from scripts.deploy import deploy
from scripts.helper_scripts import get_account
from web3 import Web3
import pytest


def test_join_submit_numbers():
    #   dealer is going to join game after starting it
    # then 3 other players will join the game
    # a seventh player will try to join the game but will not be able to
    dealerAcct1 = get_account(index=0)
    playerAcct1 = dealerAcct1  # dealer is also player 1
    playerAcct2 = get_account(index=1)
    playerAcct3 = get_account(index=2)
    playerAcct4 = get_account(index=3)

    try:
        cryptoRoulette = CryptoRoulette[-1]
    except IndexError:
        cryptoRoulette = deploy(dealerAcct1)

    dealerFees = cryptoRoulette.getDealerFeeBalance({"from": dealerAcct1})
    print("Dealer fees", dealerFees)
    contractBalance = cryptoRoulette.getCryptoRouletteBalance({"from": dealerAcct1})
    print("contractbalance", contractBalance)

    newGameKey = "mynewgamekey"  # needs to be changed each run on same contract
    ante = Web3.toWei(0.01, "ether")
    cryptoRoulette.startNewGame(ante, newGameKey, {"from": dealerAcct1, "value": ante})
    games = cryptoRoulette.getGames(True)
    game_added = newGameKey in games
    if game_added:
        dealerFees = cryptoRoulette.getDealerFeeBalance({"from": dealerAcct1})
        print("Dealer fees", dealerFees)

        contractBalance = cryptoRoulette.getCryptoRouletteBalance({"from": dealerAcct1})
        print("contractbalance", contractBalance)

        fee = cryptoRoulette.getPlayerFee(newGameKey)
        cryptoRoulette.joinGame(newGameKey, {"from": playerAcct1, "value": fee})
        cryptoRoulette.joinGame(newGameKey, {"from": playerAcct2, "value": fee})
        cryptoRoulette.joinGame(newGameKey, {"from": playerAcct3, "value": fee})
        cryptoRoulette.joinGame(newGameKey, {"from": playerAcct4, "value": fee})

        contractBalance = cryptoRoulette.getCryptoRouletteBalance({"from": dealerAcct1})
        print("contractbalance", contractBalance)

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

        # player submits number before set to in progress
        # should throw error
        highLowplayerAcct4 = 1
        oddEvenplayerAcct4 = 1
        # the 33 should not be recorded because it is an extra number
        # only 10 numbers allowed
        numbersplayerAcct4 = [2, 5, 7, 11, 14, 18, 22, 25, 28, 30, 33]

        with pytest.raises(exceptions.VirtualMachineError):
            cryptoRoulette.submitNumbers(
                newGameKey,
                highLowplayerAcct4,
                oddEvenplayerAcct4,
                numbersplayerAcct4,
                {"from": playerAcct4},
            )

        # a player other than the dealer tries to set the game in progress
        # should throw an error
        with pytest.raises(exceptions.VirtualMachineError):
            cryptoRoulette.setGameToInProgress(newGameKey, {"from": playerAcct4})

        # dealer is setting game status to in progress
        cryptoRoulette.setGameToInProgress(newGameKey, {"from": dealerAcct1})

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
        assert gameStatus == "In progress", "Game not In progress"

        cryptoRoulette.submitNumbers(
            newGameKey,
            highLowplayerAcct4,
            oddEvenplayerAcct4,
            numbersplayerAcct4,
            {"from": playerAcct4},
        )

        (round, playerAcct4picks) = cryptoRoulette.getPlayerPicks(
            newGameKey, playerAcct4
        )
        print("playerAcct4")
        print(round, playerAcct4picks)
        assert round == 1, "Incorrect round number"
        assert playerAcct4picks == (
            1,
            1,
            2,
            5,
            7,
            11,
            14,
            18,
            22,
            25,
            28,
            30,
        ), "Incorrect numbers for player 4"

        highLowplayerAcct3 = 1
        oddEvenplayerAcct3 = 0
        numbersplayerAcct3 = [2, 6, 7, 9, 11, 13, 16, 31, 33, 36]

        cryptoRoulette.submitNumbers(
            newGameKey,
            highLowplayerAcct3,
            oddEvenplayerAcct3,
            numbersplayerAcct3,
            {"from": playerAcct3},
        )

        (round, playerAcct3picks) = cryptoRoulette.getPlayerPicks(
            newGameKey, playerAcct3
        )
        print("playerAcct3")
        print(round, playerAcct3picks)
        assert playerAcct3picks == (
            1,
            0,
            2,
            6,
            7,
            9,
            11,
            13,
            16,
            31,
            33,
            36,
        ), "Incorrect numbers for player 3"

        highLowplayerAcct2 = 0
        oddEvenplayerAcct2 = 1
        numbersplayerAcct2 = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

        cryptoRoulette.submitNumbers(
            newGameKey,
            highLowplayerAcct2,
            oddEvenplayerAcct2,
            numbersplayerAcct2,
            {"from": playerAcct2},
        )

        (round, playerAcct2picks) = cryptoRoulette.getPlayerPicks(
            newGameKey, playerAcct2
        )
        print("playerAcct2")
        print(round, playerAcct2picks)
        assert playerAcct2picks == (
            0,
            1,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
        ), "Incorrect numbers for player 2"
        # dealer tries to spin wheel before all players submit numbers
        # this should throw an error

        with pytest.raises(exceptions.VirtualMachineError):
            cryptoRoulette.spinWheel(newGameKey, {"from": dealerAcct1})

        highLowplayerAcct1 = 0
        oddEvenplayerAcct1 = 0
        numbersplayerAcct1 = [2, 3, 5, 6, 8, 9, 12, 13, 15, 16]

        cryptoRoulette.submitNumbers(
            newGameKey,
            highLowplayerAcct1,
            oddEvenplayerAcct1,
            numbersplayerAcct1,
            {"from": playerAcct1},
        )

        (round, playerAcct1picks) = cryptoRoulette.getPlayerPicks(
            newGameKey, playerAcct1
        )
        print("playerAcct1")
        print(round, playerAcct1picks)
        assert playerAcct1picks == (
            0,
            0,
            2,
            3,
            5,
            6,
            8,
            9,
            12,
            13,
            15,
            16,
        ), "Incorrect numbers for player 2"
