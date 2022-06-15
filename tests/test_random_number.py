from brownie import RandomNumber
from scripts.deploy_random_number import deploy
from scripts.helper_scripts import get_account, CURRENT_GAME_KEY
from web3 import Web3
from datetime import datetime
import time


def test_RN_deploy():
    randomNumber = deploy()
    print(randomNumber)


def test_get_RN_numbers():
    account = get_account(configkey="private_key_player1")
    randomNumber = RandomNumber[-1]
    print(randomNumber)
    randomNumber.requestRandomNumbers("myrandnumkey2", 10, {"from": account})

    numbers_returned = False
    counter = 0
    while numbers_returned == False:
        numbers = randomNumber.retrieveRandomNumbers("myrandnumkey2", {"from": account})
        if len(numbers) > 0:
            print(numbers)
            break
        else:
            counter += 1
            if counter > 20:
                print("no numbers")
                break
            time.sleep(10)


def test_add_address():
    account = get_account(configkey="private_key_player1")
    randomNumber = RandomNumber[-1]
    print(randomNumber)
    randomNumber.setWhitelistAddress(
        "0xaaF034f747fC8b3f0403D61470ac240343272DE5", True, {"from": account}
    )
