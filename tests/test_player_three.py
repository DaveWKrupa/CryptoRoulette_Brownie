from brownie import CryptoRoulette
from scripts.helper_scripts import (
    get_account,
    CURRENT_GAME_KEY,
    HIGHLOW_HIGH,
    HIGHLOW_LOW,
    ODDEVEN_ODD,
    ODDEVEN_EVEN,
)


def test_player_three_join_game():
    #   dealer is going to join game after starting it
    # everything should work
    playerName = "0xeB5...A8c1D"
    account = get_account(configkey="private_key_player3")

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


def test_player3_withdraw():
    account = get_account(configkey="private_key_player3")

    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)

    cryptoRoulette.withdrawalStack(CURRENT_GAME_KEY, {"from": account})
    print("done")


def test_player3_round_1():

    acct3_rnd1_highlow = HIGHLOW_LOW
    acct3_rnd1_oddeven = ODDEVEN_ODD
    acct3_rnd1_numbers = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]

    account = get_account(configkey="private_key_player3")

    cryptoRoulette = CryptoRoulette[-1]
    print(cryptoRoulette)

    submitTransaction = cryptoRoulette.submitNumbers(
        CURRENT_GAME_KEY,
        acct3_rnd1_highlow,
        acct3_rnd1_oddeven,
        acct3_rnd1_numbers,
        {"from": account},
    )

    playersubmit = submitTransaction.events["playerSubmittedNumbers"]["player"]
    highLow = submitTransaction.events["playerSubmittedNumbers"]["highLow"]
    oddeven = submitTransaction.events["playerSubmittedNumbers"]["oddEven"]
    numbers = submitTransaction.events["playerSubmittedNumbers"]["numbers"]
    playersStack = submitTransaction.events["playerSubmittedNumbers"]["playersStack"]

    print("player submit 3")
    print(playersubmit)
    print(highLow, oddeven)
    print(numbers)
    print(playersStack)

    picks = cryptoRoulette.getPlayerPicks(CURRENT_GAME_KEY, 1, account)
    print("playerAcct3 r1")
    print(picks)
