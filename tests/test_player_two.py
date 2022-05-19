from brownie import exceptions, CryptoRoulette
from scripts.deploy import deploy
from scripts.helper_scripts import get_account
from web3 import Web3
import pytest


def test_join_end_game_and_withdrawal():
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

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack")
        print(playerAddresses)
        print(playerStacks)

        # player 4 should not be able to end the game
        with pytest.raises(exceptions.VirtualMachineError):
            cryptoRoulette.endGame({"from": playerAcct4})

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
        assert gameStatus != "Game ended", "Game ended by someone other than dealer"

        # player 4 tries to withdraw money before the game has ended
        # should not be allowed
        with pytest.raises(exceptions.VirtualMachineError):
            cryptoRoulette.withdrawalStack(newGameKey, {"from": playerAcct4})

        # end the game using the dealer account
        cryptoRoulette.endGame({"from": dealerAcct1})

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
        assert gameStatus == "Game ended", "Game not ended"

        # need to withdraw the money for each player
        # make sure their balance is 0
        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print(playerAddresses)
        print(playerStacks)

        contractBalance = cryptoRoulette.getCryptoRouletteBalance({"from": dealerAcct1})
        print("contractbalance", contractBalance)

        cryptoRoulette.withdrawalStack(newGameKey, {"from": playerAcct4})

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print(playerAddresses)
        print(playerStacks)

        contractBalance = cryptoRoulette.getCryptoRouletteBalance({"from": dealerAcct1})
        print("contractbalance", contractBalance)

        cryptoRoulette.withdrawalStack(newGameKey, {"from": playerAcct3})

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print(playerAddresses)
        print(playerStacks)

        contractBalance = cryptoRoulette.getCryptoRouletteBalance({"from": dealerAcct1})
        print("contractbalance", contractBalance)

        cryptoRoulette.withdrawalStack(newGameKey, {"from": playerAcct2})

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print(playerAddresses)
        print(playerStacks)

        contractBalance = cryptoRoulette.getCryptoRouletteBalance({"from": dealerAcct1})
        print("contractbalance", contractBalance)

        cryptoRoulette.withdrawalStack(newGameKey, {"from": playerAcct1})

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print(playerAddresses)
        print(playerStacks)

        contractBalance = cryptoRoulette.getCryptoRouletteBalance({"from": dealerAcct1})
        print("contractbalance", contractBalance)

        dealerFees = cryptoRoulette.getDealerFeeBalance({"from": dealerAcct1})
        print("Dealer fees", dealerFees)

        cryptoRoulette.withdrawDealerFees({"from": dealerAcct1})

        contractBalance = cryptoRoulette.getCryptoRouletteBalance({"from": dealerAcct1})
        print("contractbalance", contractBalance)

        dealerFees = cryptoRoulette.getDealerFeeBalance({"from": dealerAcct1})
        print("Dealer fees", dealerFees)

        assert contractBalance == 0, "contractBalance incorrect"
        assert dealerFees == 0, "dealerFees incorrect"
