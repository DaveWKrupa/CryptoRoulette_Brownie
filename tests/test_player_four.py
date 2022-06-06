from brownie import CryptoRoulette
from scripts.helper_scripts import (
    get_account,
    CURRENT_GAME_KEY,
    HIGHLOW_HIGH,
    HIGHLOW_LOW,
    ODDEVEN_ODD,
    ODDEVEN_EVEN,
)


def test_player_four_join_game():
    #   dealer is going to join game after starting it
    # everything should work
    playerName = "0x3BB...98C00"
    account = get_account(configkey="private_key_player4")

    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)

    newGameKey = CURRENT_GAME_KEY
    fee = cryptoRoulette.getPlayerFee(newGameKey)
    print(fee)

    joinGameTransaction = cryptoRoulette.joinGame(
        newGameKey, playerName, {"from": account, "value": fee}
    )
    print(joinGameTransaction)

    player = joinGameTransaction.events["playerJoined"]["player"]
    gameKey = joinGameTransaction.events["playerJoined"]["gameKey"]
    timestamp = joinGameTransaction.events["playerJoined"]["timeStamp"]
    print("join event")
    print(player, gameKey, timestamp)


def test_player4_withdraw():
    account = get_account(configkey="private_key_player4")

    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)

    cryptoRoulette.withdrawalStack(CURRENT_GAME_KEY, {"from": account})
    print("done")


def test_player4_round_1():

    acct4_rnd1_highlow = HIGHLOW_LOW
    acct4_rnd1_oddeven = ODDEVEN_EVEN
    acct4_rnd1_numbers = [4, 8, 12, 16, 19, 27, 29, 31, 35, 36]

    account = get_account(configkey="private_key_player4")

    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)

    submitTransaction = cryptoRoulette.submitNumbers(
        CURRENT_GAME_KEY,
        acct4_rnd1_highlow,
        acct4_rnd1_oddeven,
        acct4_rnd1_numbers,
        {"from": account},
    )

    playersubmit = submitTransaction.events["playerSubmittedNumbers"]["player"]
    highLow = submitTransaction.events["playerSubmittedNumbers"]["highLow"]
    oddeven = submitTransaction.events["playerSubmittedNumbers"]["oddEven"]
    numbers = submitTransaction.events["playerSubmittedNumbers"]["numbers"]
    playersStack = submitTransaction.events["playerSubmittedNumbers"]["playersStack"]

    print("player submit 4")
    print(playersubmit)
    print(highLow, oddeven)
    print(numbers)
    print(playersStack)

    picks = cryptoRoulette.getPlayerPicks(CURRENT_GAME_KEY, 1, account)
    print("playerAcct4 r1")
    print(picks)
