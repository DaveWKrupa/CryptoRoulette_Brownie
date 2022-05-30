from brownie import CryptoRoulette
from scripts.deploy import deploy
from scripts.helper_scripts import (
    get_account,
)
from web3 import Web3
from datetime import datetime
import time


def test_rinkeby_deploy():

    high = 0
    low = 1
    odd = 0
    even = 1
    #   dealer is going to join game after starting it
    # then 3 other players will join the game

    dealerAcct1 = get_account(configkey="private_key_player1")
    playerAcct1 = dealerAcct1  # dealer is also player 1
    playerAcct2 = get_account(configkey="private_key_player2")
    playerAcct3 = get_account(configkey="private_key_player3")
    playerAcct4 = get_account(configkey="private_key_player4")

    crypto_roulette = deploy()
    # crypto_roulette = CryptoRoulette[-1]

    print(crypto_roulette)

    newGameKey = (
        str(dealerAcct1)[:5]
        + "..."
        + str(dealerAcct1)[len(str(dealerAcct1)) - 5 : len(str(dealerAcct1))]
        + "_"
        + str(datetime.utcnow())
    )

    ante = Web3.toWei(0.001, "ether")
    dealerfee = crypto_roulette.getDealerFee()
    start_game_tx = crypto_roulette.startNewGame(
        ante,
        newGameKey,
        {"from": dealerAcct1, "value": dealerfee},
    )
    # "gasPrice": 1000000000000000000
    # message = crypto_roulette.getTheMessage()
    # print(message)
    newgamedealer = start_game_tx.events["newGameStarted"]["dealer"]
    newgamegameKey = start_game_tx.events["newGameStarted"]["gameKey"]
    newgametimeStamp = start_game_tx.events["newGameStarted"]["timeStamp"]
    newgameante = start_game_tx.events["newGameStarted"]["ante"]
    print("new game event / change status event")
    newstatus = start_game_tx.events["gameStatusChanged"]["newStatus"]
    print(newgamedealer, newgamegameKey, newgametimeStamp, newgameante, newstatus)

    games = crypto_roulette.getGames(True)
    game_added = newGameKey in games

    if game_added:
        # dealerFees = crypto_roulette.getDealerFeeBalance({"from": dealerAcct1})
        # print("Dealer fee balance", dealerFees)

        # contractBalance = crypto_roulette.getCryptoRouletteBalance(
        #     {"from": dealerAcct1}
        # )
        # print("contractbalance", contractBalance)

        fee = crypto_roulette.getPlayerFee(newGameKey)
        joinGameTransaction = crypto_roulette.joinGame(
            newGameKey, {"from": playerAcct1, "value": fee}
        )

        player = joinGameTransaction.events["playerJoined"]["player"]
        gameKey = joinGameTransaction.events["playerJoined"]["gameKey"]
        timestamp = joinGameTransaction.events["playerJoined"]["timeStamp"]
        print("join event 1")
        print(player, gameKey, timestamp)

        joinGameTransaction = crypto_roulette.joinGame(
            newGameKey, {"from": playerAcct2, "value": fee}
        )

        player = joinGameTransaction.events["playerJoined"]["player"]
        gameKey = joinGameTransaction.events["playerJoined"]["gameKey"]
        timestamp = joinGameTransaction.events["playerJoined"]["timeStamp"]
        print("join event 1")
        print(player, gameKey, timestamp)

        joinGameTransaction = crypto_roulette.joinGame(
            newGameKey, {"from": playerAcct3, "value": fee}
        )

        player = joinGameTransaction.events["playerJoined"]["player"]
        gameKey = joinGameTransaction.events["playerJoined"]["gameKey"]
        timestamp = joinGameTransaction.events["playerJoined"]["timeStamp"]
        print("join event 1")
        print(player, gameKey, timestamp)

        joinGameTransaction = crypto_roulette.joinGame(
            newGameKey, {"from": playerAcct4, "value": fee}
        )

        player = joinGameTransaction.events["playerJoined"]["player"]
        gameKey = joinGameTransaction.events["playerJoined"]["gameKey"]
        timestamp = joinGameTransaction.events["playerJoined"]["timeStamp"]
        print("join event 1")
        print(player, gameKey, timestamp)

        contractBalance = crypto_roulette.getCryptoRouletteBalance(
            {"from": dealerAcct1}
        )
        print("contractbalance", contractBalance)

        (
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        ) = crypto_roulette.getGameInfo(newGameKey)

        print(
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        )

        # dealer is setting game status to in progress
        set_in_progress_tx = crypto_roulette.setGameToInProgress(
            newGameKey, {"from": dealerAcct1}
        )

        newstatus = set_in_progress_tx.events["gameStatusChanged"]["newStatus"]
        print("set inprogress status event", newstatus)

        (
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        ) = crypto_roulette.getGameInfo(newGameKey)

        print(
            dealer,
            ante,
            gameStatus,
            potAmount,
            playerCount,
            currentRound,
        )

        (playerAddresses, playerStacks) = crypto_roulette.getGamePlayers(newGameKey)
        print("address and stack before game")
        print(playerAddresses)
        print(playerStacks)

        ###################################################################################
        # Round 1

        currentRound = 1
        print(f"round {currentRound}")

        acct1_rnd1_highlow = high
        acct2_rnd1_highlow = high
        acct3_rnd1_highlow = low
        acct4_rnd1_highlow = low

        acct1_rnd1_oddeven = even
        acct2_rnd1_oddeven = odd
        acct3_rnd1_oddeven = odd
        acct4_rnd1_oddeven = even

        acct1_rnd1_numbers = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        acct2_rnd1_numbers = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        acct3_rnd1_numbers = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
        acct4_rnd1_numbers = [4, 8, 12, 16, 19, 27, 29, 31, 35, 36]

        # player 1

        submitTransaction = crypto_roulette.submitNumbers(
            newGameKey,
            acct1_rnd1_highlow,
            acct1_rnd1_oddeven,
            acct1_rnd1_numbers,
            {"from": playerAcct1},
        )

        playerAcct1picks = crypto_roulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct1
        )
        print("playerAcct1 r1")
        print(playerAcct1picks)

        # player 2

        crypto_roulette.submitNumbers(
            newGameKey,
            acct2_rnd1_highlow,
            acct2_rnd1_oddeven,
            acct2_rnd1_numbers,
            {"from": playerAcct2},
        )

        playerAcct2picks = crypto_roulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct2
        )
        print("playerAcct2 r1")
        print(playerAcct2picks)

        # player 3

        crypto_roulette.submitNumbers(
            newGameKey,
            acct3_rnd1_highlow,
            acct3_rnd1_oddeven,
            acct3_rnd1_numbers,
            {"from": playerAcct3},
        )

        playerAcct3picks = crypto_roulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct3
        )
        print("playerAcct3 r1")
        print(playerAcct3picks)

        # player 4

        crypto_roulette.submitNumbers(
            newGameKey,
            acct4_rnd1_highlow,
            acct4_rnd1_oddeven,
            acct4_rnd1_numbers,
            {"from": playerAcct4},
        )

        playerAcct4picks = crypto_roulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct4
        )
        print("playerAcct4 r1")
        print(playerAcct4picks)

        print("winning number r1")
        counter = 0
        time.sleep(5)  # give it some time to get the random number from Chainlink
        winning_number = crypto_roulette.getWinningNumber(newGameKey, 1)
        while winning_number == 0:
            time.sleep(5)
            winning_number = crypto_roulette.getWinningNumber(newGameKey, 1)
            counter += 1
            if counter > 20:
                break

        print(winning_number)

        (playerAddresses, playerStacks) = crypto_roulette.getGamePlayers(newGameKey)
        print("address and stack r1")
        print(playerAddresses)
        print(playerStacks)
