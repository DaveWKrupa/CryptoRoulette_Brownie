from brownie import exceptions, network
from scripts.deploy import deploy
from scripts.helper_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from web3 import Web3
import pytest


def test_full_game():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return

    high = 0
    low = 1
    odd = 0
    even = 1
    #   dealer is going to join game after starting it
    # then 3 other players will join the game
    # a seventh player will try to join the game but will not be able to
    dealerAcct1 = get_account(index=0)
    playerAcct1 = dealerAcct1  # dealer is also player 1
    playerAcct2 = get_account(index=1)
    playerAcct3 = get_account(index=2)
    playerAcct4 = get_account(index=3)

    cryptoRoulette = deploy()

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

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
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

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct1_rnd1_highlow,
            acct1_rnd1_oddeven,
            acct1_rnd1_numbers,
            {"from": playerAcct1},
        )

        playerAcct1picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct1
        )
        print("playerAcct1 r1")
        print(playerAcct1picks)

        # player 2

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct2_rnd1_highlow,
            acct2_rnd1_oddeven,
            acct2_rnd1_numbers,
            {"from": playerAcct2},
        )

        playerAcct2picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct2
        )
        print("playerAcct2 r1")
        print(playerAcct2picks)

        # player 3

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct3_rnd1_highlow,
            acct3_rnd1_oddeven,
            acct3_rnd1_numbers,
            {"from": playerAcct3},
        )

        playerAcct3picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct3
        )
        print("playerAcct3 r1")
        print(playerAcct3picks)

        # player 4

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct4_rnd1_highlow,
            acct4_rnd1_oddeven,
            acct4_rnd1_numbers,
            {"from": playerAcct4},
        )

        playerAcct4picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct4
        )
        print("playerAcct4 r1")
        print(playerAcct4picks)

        print("winning number r1")
        print(cryptoRoulette.getWinningNumber(newGameKey, 1))

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack r1")
        print(playerAddresses)
        print(playerStacks)

        ###################################################################################

        # Round 2
        currentRound = 2
        print(f"round {currentRound}")

        acct1_rnd2_highlow = low
        acct2_rnd2_highlow = high
        acct3_rnd2_highlow = high
        acct4_rnd2_highlow = low

        acct1_rnd2_oddeven = even
        acct2_rnd2_oddeven = odd
        acct3_rnd2_oddeven = odd
        acct4_rnd2_oddeven = even

        acct1_rnd2_numbers = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        acct2_rnd2_numbers = [27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        acct3_rnd2_numbers = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        acct4_rnd2_numbers = [1, 6, 9, 12, 15, 17, 18, 21, 27, 33]

        # player 1

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct1_rnd2_highlow,
            acct1_rnd2_oddeven,
            acct1_rnd2_numbers,
            {"from": playerAcct1},
        )

        playerAcct1picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct1
        )
        print("playerAcct1 r2")
        print(playerAcct1picks)

        # player 2

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct2_rnd2_highlow,
            acct2_rnd2_oddeven,
            acct2_rnd2_numbers,
            {"from": playerAcct2},
        )

        playerAcct2picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct2
        )
        print("playerAcct2 r2")
        print(playerAcct2picks)

        # player 3

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct3_rnd2_highlow,
            acct3_rnd2_oddeven,
            acct3_rnd2_numbers,
            {"from": playerAcct3},
        )

        playerAcct3picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct3
        )
        print("playerAcct3 r2")
        print(playerAcct3picks)

        # player 4

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct4_rnd2_highlow,
            acct4_rnd2_oddeven,
            acct4_rnd2_numbers,
            {"from": playerAcct4},
        )

        playerAcct4picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct4
        )
        print("playerAcct4 r2")
        print(playerAcct4picks)

        print("winning number r2")
        print(cryptoRoulette.getWinningNumber(newGameKey, 1))

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack r2")
        print(playerAddresses)
        print(playerStacks)

        ###################################################################################
        # Round 3
        currentRound = 3
        print(f"round {currentRound}")

        acct1_rnd3_highlow = high
        acct2_rnd3_highlow = low
        acct3_rnd3_highlow = high
        acct4_rnd3_highlow = high

        acct1_rnd3_oddeven = even
        acct2_rnd3_oddeven = even
        acct3_rnd3_oddeven = odd
        acct4_rnd3_oddeven = even

        acct1_rnd3_numbers = [27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        acct2_rnd3_numbers = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        acct3_rnd3_numbers = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        acct4_rnd3_numbers = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]

        # player 1

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct1_rnd3_highlow,
            acct1_rnd3_oddeven,
            acct1_rnd3_numbers,
            {"from": playerAcct1},
        )

        playerAcct1picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct1
        )
        print("playerAcct1 r3")
        print(playerAcct1picks)

        # player 2

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct2_rnd3_highlow,
            acct2_rnd3_oddeven,
            acct2_rnd3_numbers,
            {"from": playerAcct2},
        )

        playerAcct2picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct2
        )
        print("playerAcct2 r3")
        print(playerAcct2picks)

        # player 3

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct3_rnd3_highlow,
            acct3_rnd3_oddeven,
            acct3_rnd3_numbers,
            {"from": playerAcct3},
        )

        playerAcct3picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct3
        )
        print("playerAcct3 r3")
        print(playerAcct3picks)

        # player 4

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct4_rnd3_highlow,
            acct4_rnd3_oddeven,
            acct4_rnd3_numbers,
            {"from": playerAcct4},
        )

        playerAcct4picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct4
        )
        print("playerAcct4 r3")
        print(playerAcct4picks)

        print("winning number r3")
        print(cryptoRoulette.getWinningNumber(newGameKey, 1))

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack r3")
        print(playerAddresses)
        print(playerStacks)

        ###################################################################################

        # Round 4
        currentRound = 4
        print(f"round {currentRound}")

        acct1_rnd4_highlow = low
        acct2_rnd4_highlow = high
        acct3_rnd4_highlow = low
        acct4_rnd4_highlow = low

        acct1_rnd4_oddeven = even
        acct2_rnd4_oddeven = odd
        acct3_rnd4_oddeven = odd
        acct4_rnd4_oddeven = even

        acct1_rnd4_numbers = [4, 8, 12, 16, 19, 27, 29, 31, 35, 36]
        acct2_rnd4_numbers = [1, 6, 9, 12, 15, 17, 18, 21, 27, 33]
        acct3_rnd4_numbers = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        acct4_rnd4_numbers = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

        # player 1

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct1_rnd4_highlow,
            acct1_rnd4_oddeven,
            acct1_rnd4_numbers,
            {"from": playerAcct1},
        )

        playerAcct1picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct1
        )
        print("playerAcct1 r4")
        print(playerAcct1picks)

        # player 2

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct2_rnd4_highlow,
            acct2_rnd4_oddeven,
            acct2_rnd4_numbers,
            {"from": playerAcct2},
        )

        playerAcct2picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct2
        )
        print("playerAcct2 r4")
        print(playerAcct2picks)

        # player 3

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct3_rnd4_highlow,
            acct3_rnd4_oddeven,
            acct3_rnd4_numbers,
            {"from": playerAcct3},
        )

        playerAcct3picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct3
        )
        print("playerAcct3 r4")
        print(playerAcct3picks)

        # player 4

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct4_rnd4_highlow,
            acct4_rnd4_oddeven,
            acct4_rnd4_numbers,
            {"from": playerAcct4},
        )

        playerAcct4picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct4
        )
        print("playerAcct4 r4")
        print(playerAcct4picks)

        print("winning number r4")
        print(cryptoRoulette.getWinningNumber(newGameKey, 1))

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack r4")
        print(playerAddresses)
        print(playerStacks)

        ###################################################################################

        # Round 5
        currentRound = 5
        print(f"round {currentRound}")

        acct1_rnd5_highlow = high
        acct2_rnd5_highlow = high
        acct3_rnd5_highlow = low
        acct4_rnd5_highlow = high

        acct1_rnd5_oddeven = odd
        acct2_rnd5_oddeven = odd
        acct3_rnd5_oddeven = odd
        acct4_rnd5_oddeven = even

        acct1_rnd5_numbers = [1, 6, 9, 12, 15, 17, 18, 21, 27, 33]
        acct2_rnd5_numbers = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        acct3_rnd5_numbers = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        acct4_rnd5_numbers = [27, 28, 29, 30, 31, 32, 33, 34, 35, 36]

        # player 1

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct1_rnd5_highlow,
            acct1_rnd5_oddeven,
            acct1_rnd5_numbers,
            {"from": playerAcct1},
        )

        playerAcct1picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct1
        )
        print("playerAcct1 r5")
        print(playerAcct1picks)

        # player 2

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct2_rnd5_highlow,
            acct2_rnd5_oddeven,
            acct2_rnd5_numbers,
            {"from": playerAcct2},
        )

        playerAcct2picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct2
        )
        print("playerAcct2 r5")
        print(playerAcct2picks)

        # player 3

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct3_rnd5_highlow,
            acct3_rnd5_oddeven,
            acct3_rnd5_numbers,
            {"from": playerAcct3},
        )

        playerAcct3picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct3
        )
        print("playerAcct3 r5")
        print(playerAcct3picks)

        # player 4

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct4_rnd5_highlow,
            acct4_rnd5_oddeven,
            acct4_rnd5_numbers,
            {"from": playerAcct4},
        )

        playerAcct4picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct4
        )
        print("playerAcct4 r5")
        print(playerAcct4picks)

        print("winning number r5")
        print(cryptoRoulette.getWinningNumber(newGameKey, 1))

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack r")
        print(playerAddresses)
        print(playerStacks)

        ###################################################################################

        # Round 6
        currentRound = 6
        print(f"round {currentRound}")

        acct1_rnd6_highlow = low
        acct2_rnd6_highlow = high
        acct3_rnd6_highlow = low
        acct4_rnd6_highlow = low

        acct1_rnd6_oddeven = odd
        acct2_rnd6_oddeven = even
        acct3_rnd6_oddeven = even
        acct4_rnd6_oddeven = odd

        acct1_rnd6_numbers = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
        acct2_rnd6_numbers = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        acct3_rnd6_numbers = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        acct4_rnd6_numbers = [4, 8, 12, 16, 19, 27, 29, 31, 35, 36]

        # player 1

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct1_rnd6_highlow,
            acct1_rnd6_oddeven,
            acct1_rnd6_numbers,
            {"from": playerAcct1},
        )

        playerAcct1picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct1
        )
        print("playerAcct1 r6")
        print(playerAcct1picks)

        # player 2

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct2_rnd6_highlow,
            acct2_rnd6_oddeven,
            acct2_rnd6_numbers,
            {"from": playerAcct2},
        )

        playerAcct2picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct2
        )
        print("playerAcct2 r6")
        print(playerAcct2picks)

        # player 3

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct3_rnd6_highlow,
            acct3_rnd6_oddeven,
            acct3_rnd6_numbers,
            {"from": playerAcct3},
        )

        playerAcct3picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct3
        )
        print("playerAcct3 r6")
        print(playerAcct3picks)

        # player 4

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct4_rnd6_highlow,
            acct4_rnd6_oddeven,
            acct4_rnd6_numbers,
            {"from": playerAcct4},
        )

        playerAcct4picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct4
        )
        print("playerAcct4 r6")
        print(playerAcct4picks)

        print("winning number r6")
        print(cryptoRoulette.getWinningNumber(newGameKey, 1))

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack r6")
        print(playerAddresses)
        print(playerStacks)

        ###################################################################################

        # Round 7
        currentRound = 7
        print(f"round {currentRound}")

        acct1_rnd7_highlow = high
        acct2_rnd7_highlow = high
        acct3_rnd7_highlow = low
        acct4_rnd7_highlow = low

        acct1_rnd7_oddeven = odd
        acct2_rnd7_oddeven = even
        acct3_rnd7_oddeven = odd
        acct4_rnd7_oddeven = even

        acct1_rnd7_numbers = [6, 7, 9, 11, 15, 18, 24, 27, 32, 33]
        acct2_rnd7_numbers = [4, 8, 12, 16, 19, 27, 29, 31, 35, 36]
        acct3_rnd7_numbers = [1, 6, 9, 12, 15, 17, 18, 21, 27, 33]
        acct4_rnd7_numbers = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        # player 1

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct1_rnd7_highlow,
            acct1_rnd7_oddeven,
            acct1_rnd7_numbers,
            {"from": playerAcct1},
        )

        playerAcct1picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct1
        )
        print("playerAcct1 r7")
        print(playerAcct1picks)

        # player 2

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct2_rnd7_highlow,
            acct2_rnd7_oddeven,
            acct2_rnd7_numbers,
            {"from": playerAcct2},
        )

        playerAcct2picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct2
        )
        print("playerAcct2 r7")
        print(playerAcct2picks)

        # player 3

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct3_rnd7_highlow,
            acct3_rnd7_oddeven,
            acct3_rnd7_numbers,
            {"from": playerAcct3},
        )

        playerAcct3picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct3
        )
        print("playerAcct3 r7")
        print(playerAcct3picks)

        # player 4

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct4_rnd7_highlow,
            acct4_rnd7_oddeven,
            acct4_rnd7_numbers,
            {"from": playerAcct4},
        )

        playerAcct4picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct4
        )
        print("playerAcct4 r7")
        print(playerAcct4picks)

        print("winning number r7")
        print(cryptoRoulette.getWinningNumber(newGameKey, 1))

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack r7")
        print(playerAddresses)
        print(playerStacks)

        ###################################################################################

        # Round 8
        currentRound = 8
        print(f"round {currentRound}")

        acct1_rnd8_highlow = high
        acct2_rnd8_highlow = high
        acct3_rnd8_highlow = high
        acct4_rnd8_highlow = low

        acct1_rnd8_oddeven = odd
        acct2_rnd8_oddeven = odd
        acct3_rnd8_oddeven = odd
        acct4_rnd8_oddeven = even

        acct1_rnd8_numbers = [27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        acct2_rnd8_numbers = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        acct3_rnd8_numbers = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        acct4_rnd8_numbers = [4, 8, 12, 16, 19, 27, 29, 31, 35, 36]

        # player 1

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct1_rnd8_highlow,
            acct1_rnd8_oddeven,
            acct1_rnd8_numbers,
            {"from": playerAcct1},
        )

        playerAcct1picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct1
        )
        print("playerAcct1 r8")
        print(playerAcct1picks)

        # player 2

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct2_rnd8_highlow,
            acct2_rnd8_oddeven,
            acct2_rnd8_numbers,
            {"from": playerAcct2},
        )

        playerAcct2picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct2
        )
        print("playerAcct2 r8")
        print(playerAcct2picks)

        # player 3

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct3_rnd8_highlow,
            acct3_rnd8_oddeven,
            acct3_rnd8_numbers,
            {"from": playerAcct3},
        )

        playerAcct3picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct3
        )
        print("playerAcct3 r8")
        print(playerAcct3picks)

        # player 4

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct4_rnd8_highlow,
            acct4_rnd8_oddeven,
            acct4_rnd8_numbers,
            {"from": playerAcct4},
        )

        playerAcct4picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct4
        )
        print("playerAcct4 r8")
        print(playerAcct4picks)

        print("winning number r8")
        print(cryptoRoulette.getWinningNumber(newGameKey, 1))

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack r8")
        print(playerAddresses)
        print(playerStacks)

        ###################################################################################

        # Round 9
        currentRound = 9
        print(f"round {currentRound}")

        acct1_rnd9_highlow = high
        acct2_rnd9_highlow = high
        acct3_rnd9_highlow = low
        acct4_rnd9_highlow = low

        acct1_rnd9_oddeven = odd
        acct2_rnd9_oddeven = even
        acct3_rnd9_oddeven = odd
        acct4_rnd9_oddeven = even

        acct1_rnd9_numbers = [1, 6, 9, 12, 15, 17, 18, 21, 27, 33]
        acct2_rnd9_numbers = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
        acct3_rnd9_numbers = [27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        acct4_rnd9_numbers = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

        # player 1

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct1_rnd9_highlow,
            acct1_rnd9_oddeven,
            acct1_rnd9_numbers,
            {"from": playerAcct1},
        )

        playerAcct1picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct1
        )
        print("playerAcct1 r9")
        print(playerAcct1picks)

        # player 2

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct2_rnd9_highlow,
            acct2_rnd9_oddeven,
            acct2_rnd9_numbers,
            {"from": playerAcct2},
        )

        playerAcct2picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct2
        )
        print("playerAcct2 r9")
        print(playerAcct2picks)

        # player 3

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct3_rnd9_highlow,
            acct3_rnd9_oddeven,
            acct3_rnd9_numbers,
            {"from": playerAcct3},
        )

        playerAcct3picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct3
        )
        print("playerAcct3 r9")
        print(playerAcct3picks)

        # player 4

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct4_rnd9_highlow,
            acct4_rnd9_oddeven,
            acct4_rnd9_numbers,
            {"from": playerAcct4},
        )

        playerAcct4picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct4
        )
        print("playerAcct4 r9")
        print(playerAcct4picks)

        print("winning number r9")
        print(cryptoRoulette.getWinningNumber(newGameKey, 1))

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack r9")
        print(playerAddresses)
        print(playerStacks)

        ###################################################################################

        # Round 10
        currentRound = 10
        print(f"round {currentRound}")

        acct1_rnd10_highlow = high
        acct2_rnd10_highlow = high
        acct3_rnd10_highlow = low
        acct4_rnd10_highlow = low

        acct1_rnd10_oddeven = odd
        acct2_rnd10_oddeven = even
        acct3_rnd10_oddeven = odd
        acct4_rnd10_oddeven = even

        acct1_rnd10_numbers = [1, 3, 5, 7, 9, 11, 13, 15, 17, 20]
        acct2_rnd10_numbers = [4, 8, 12, 16, 18, 27, 29, 31, 35, 36]
        acct3_rnd10_numbers = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        acct4_rnd10_numbers = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]

        # player 1

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct1_rnd10_highlow,
            acct1_rnd10_oddeven,
            acct1_rnd10_numbers,
            {"from": playerAcct1},
        )

        playerAcct1picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct1
        )
        print("playerAcct1 r10")
        print(playerAcct1picks)

        # player 2

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct2_rnd10_highlow,
            acct2_rnd10_oddeven,
            acct2_rnd10_numbers,
            {"from": playerAcct2},
        )

        playerAcct2picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct2
        )
        print("playerAcct2 r10")
        print(playerAcct2picks)

        # player 3

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct3_rnd10_highlow,
            acct3_rnd10_oddeven,
            acct3_rnd10_numbers,
            {"from": playerAcct3},
        )

        playerAcct3picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct3
        )
        print("playerAcct3 r10")
        print(playerAcct3picks)

        # player 4

        cryptoRoulette.submitNumbers(
            newGameKey,
            acct4_rnd10_highlow,
            acct4_rnd10_oddeven,
            acct4_rnd10_numbers,
            {"from": playerAcct4},
        )

        playerAcct4picks = cryptoRoulette.getPlayerPicks(
            newGameKey, currentRound, playerAcct4
        )
        print("playerAcct4 r10")
        print(playerAcct4picks)

        print("winning number r10")
        print(cryptoRoulette.getWinningNumber(newGameKey, 1))

        (playerAddresses, playerStacks) = cryptoRoulette.getGamePlayers(newGameKey)
        print("address and stack r10")
        print(playerAddresses)
        print(playerStacks)

        ###################################################################################

        print("Winners And Amounts")

        (
            winners,
            winType,
            winAmount,
            winRound,
            winnerStack,
        ) = cryptoRoulette.getWinnersAndAmounts()
        winnersLength = len(winners)
        for index in range(winnersLength):
            print("***********")
            print(winners[index])
            print(winType[index])
            print(winAmount[index])
            print(winRound[index])
            print(winnerStack[index])
            print("***********")

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
        print("address and stack after game")
        print(playerAddresses)
        print(playerStacks)
