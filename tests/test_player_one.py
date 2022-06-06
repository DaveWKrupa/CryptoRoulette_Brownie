from brownie import CryptoRoulette
from scripts.helper_scripts import (
    get_account,
    CURRENT_GAME_KEY,
    HIGHLOW_HIGH,
    HIGHLOW_LOW,
    ODDEVEN_ODD,
    ODDEVEN_EVEN,
)


def test_player_one_join_game():
    #   dealer is going to join game after starting it
    # everything should work
    playerName = "0x4A2...22e85"
    account = get_account(configkey="private_key_player1")

    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)

    fee = cryptoRoulette.getPlayerFee(CURRENT_GAME_KEY)
    print(fee)

    joinGameTransaction = cryptoRoulette.joinGame(
        CURRENT_GAME_KEY, playerName, {"from": account, "value": fee}
    )
    print(joinGameTransaction)


def test_player1_withdraw():
    account = get_account(configkey="private_key_player1")

    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)

    cryptoRoulette.withdrawalStack(CURRENT_GAME_KEY, {"from": account})
    print("done")


def test_player1_round_1():

    acct1_rnd1_highlow = HIGHLOW_HIGH
    acct1_rnd1_oddeven = ODDEVEN_EVEN
    acct1_rnd1_numbers = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

    account = get_account(configkey="private_key_player1")

    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)

    submitTransaction = cryptoRoulette.submitNumbers(
        CURRENT_GAME_KEY,
        acct1_rnd1_highlow,
        acct1_rnd1_oddeven,
        acct1_rnd1_numbers,
        {"from": account},
    )

    playersubmit = submitTransaction.events["playerSubmittedNumbers"]["player"]
    highLow = submitTransaction.events["playerSubmittedNumbers"]["highLow"]
    oddeven = submitTransaction.events["playerSubmittedNumbers"]["oddEven"]
    numbers = submitTransaction.events["playerSubmittedNumbers"]["numbers"]
    playersStack = submitTransaction.events["playerSubmittedNumbers"]["playersStack"]

    print("player submit 1")
    print(playersubmit)
    print(highLow, oddeven)
    print(numbers)
    print(playersStack)

    picks = cryptoRoulette.getPlayerPicks(CURRENT_GAME_KEY, 1, account)
    print("playerAcct1 r1")
    print(picks)
