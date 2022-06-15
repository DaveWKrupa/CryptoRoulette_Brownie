from brownie import CryptoRoulette
from scripts.deploy import deploy
from scripts.helper_scripts import get_account, CURRENT_GAME_KEY
from web3 import Web3
from datetime import datetime
import time

# 0x3186390e795a374D2E5a684a06368412Da6d5DED
def test_dealer_deploy():
    cryptoRoulette = deploy()
    print(cryptoRoulette)


def test_dealer_start_game():
    # everything should work

    account = get_account(configkey="private_key_player1")

    cryptoRoulette = CryptoRoulette[-1]  # get the latest published
    print(cryptoRoulette)

    # newGameKey = (
    #     str(account)[:5]
    #     + "..."
    #     + str(account)[len(str(account)) - 5 : len(str(account))]
    #     + "_"
    #     + str(datetime.utcnow())
    # )

    # print("newGameKey")
    # print(newGameKey)

    ante = Web3.toWei(0.001, "ether")
    start_game_tx = cryptoRoulette.startNewGame(
        ante, CURRENT_GAME_KEY, {"from": account, "value": ante, "gasLimit": 10000000}
    )
    print(start_game_tx)


def test_get_numbers():
    account = get_account(configkey="private_key_player1")
    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)
    numbers = cryptoRoulette.getRandomNumbers(CURRENT_GAME_KEY, {"from": account})
    print(numbers)


def test_get_message():
    cryptoRoulette = CryptoRoulette[-1]

    message = cryptoRoulette.getMessage()
    print(message)


def test_set_ready_for_players():

    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)
    account = get_account(configkey="private_key_player1")
    gameKey = CURRENT_GAME_KEY
    # dealer is setting game status to in progress
    print("setting")
    set_in_progress_tx = cryptoRoulette.setReadyForPlayers(gameKey, {"from": account})

    print(set_in_progress_tx)


def test_set_in_progress():

    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)
    account = get_account(configkey="private_key_player1")
    gameKey = CURRENT_GAME_KEY
    # dealer is setting game status to in progress
    print("setting")
    set_in_progress_tx = cryptoRoulette.setGameToInProgress(gameKey, {"from": account})

    print(set_in_progress_tx)


def test_spin_wheel():
    account = get_account(configkey="private_key_player1")

    cryptoRoulette = CryptoRoulette[-1]  # get the latest published
    print(cryptoRoulette)
    tx = cryptoRoulette.dealerSpinWheel(CURRENT_GAME_KEY, {"from": account})
    time.sleep(10)


def test_get_games():
    cryptoRoulette = CryptoRoulette[-1]  # get the latest published
    games = cryptoRoulette.getGames(True)
    print("games")
    print(games)


def test_get_game_info():
    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)

    (
        dealer,
        ante,
        gameStatus,
        potAmount,
        playerCount,
        currentRound,
        startTime,
    ) = cryptoRoulette.getGameInfo(CURRENT_GAME_KEY)

    print("gameinfo")
    print(dealer, ante, gameStatus, potAmount, playerCount, currentRound, startTime)

    (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(CURRENT_GAME_KEY)
    print("address and stack")
    print(playerAddresses)
    print(playerStacks)
    account = get_account(configkey="private_key_player1")
    balance = cryptoRoulette.getCryptoRouletteBalance({"from": account})
    print("balance", balance)


def test_withdraw_dealer_fees():
    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)
    account = get_account(configkey="private_key_player1")
    balance = cryptoRoulette.getCryptoRouletteBalance({"from": account})
    print("getCryptoRouletteBalance", balance)
    balance = cryptoRoulette.getDealerFeeBalance({"from": account})
    print("getDealerFeeBalance", balance)

    cryptoRoulette.withdrawDealerFees({"from": account})

    balance = cryptoRoulette.getDealerFeeBalance({"from": account})
    print("getDealerFeeBalance", balance)

    balance = cryptoRoulette.getCryptoRouletteBalance({"from": account})
    print("getCryptoRouletteBalance", balance)


def test_withdraw_all():
    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)
    account = get_account(configkey="private_key_player1")
    # balance = cryptoRoulette.getCryptoRouletteBalance({"from": account})
    # print("getCryptoRouletteBalance", balance)
    cryptoRoulette.withdrawalAll({"from": account})
    # balance = cryptoRoulette.getCryptoRouletteBalance({"from": account})
    # print("getCryptoRouletteBalance", balance)


def test_clear_current_games():
    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)
    games = cryptoRoulette.getGames(True)
    print("games")
    print(games)
    account = get_account(configkey="private_key_player1")
    cryptoRoulette.clearGames({"from": account})
    time.sleep(5)
    games = cryptoRoulette.getGames(True)
    print("games")
    print(games)


def test_cancel_game():
    account = get_account(configkey="private_key_player1")
    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)
    games = cryptoRoulette.getGames(True)
    print("games")
    print(games)
    cryptoRoulette.cancelNewGame(CURRENT_GAME_KEY, {"from": account})
    games = cryptoRoulette.getGames(True)
    print("games")
    print(games)


def test_get_player_picks1():
    cryptoRoulette = CryptoRoulette[-1]

    account1 = get_account(configkey="private_key_player1")
    picks = cryptoRoulette.getPlayerPicks(CURRENT_GAME_KEY, 1, account1)
    print("playerAcct1 r1")
    print(picks)

    account2 = get_account(configkey="private_key_player2")
    picks = cryptoRoulette.getPlayerPicks(CURRENT_GAME_KEY, 1, account2)
    print("playerAcct2 r1")
    print(picks)

    account3 = get_account(configkey="private_key_player3")
    picks = cryptoRoulette.getPlayerPicks(CURRENT_GAME_KEY, 1, account3)
    print("playerAcct3 r1")
    print(picks)

    account4 = get_account(configkey="private_key_player4")
    picks = cryptoRoulette.getPlayerPicks(CURRENT_GAME_KEY, 1, account4)
    print("playerAcct4 r1")
    print(picks)
