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
        account = get_account()
        cryptoRoulette = deploy()

    newGameKey = "mynewgamekey"  # needs to be changed each run on same contract
    ante = Web3.toWei(0.01, "ether")
    cryptoRoulette.startNewGame(ante, newGameKey, {"from": account, "value": ante})
    games = cryptoRoulette.getGames(True)
    game_added = newGameKey in games
    if game_added:
        fee = cryptoRoulette.getPlayerFee(newGameKey)
        cryptoRoulette.joinGame(newGameKey, {"from": playerAcct1, "value": fee})
        cryptoRoulette.joinGame(newGameKey, {"from": playerAcct2, "value": fee})
        cryptoRoulette.joinGame(newGameKey, {"from": playerAcct3, "value": fee})
        cryptoRoulette.joinGame(newGameKey, {"from": playerAcct4, "value": fee})
