from brownie import CryptoRoulette, network, config
from web3 import Web3
from scripts.helper_scripts import (
    get_account,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)


def deploy():

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        account = get_account(index=0)
    else:
        account = get_account(configkey="private_key_player1")

    subscription_id = config["networks"][network.show_active()]["subscriptionid"]
    key_hash = config["networks"][network.show_active()]["keyhash"]
    vrf_coordinator = config["networks"][network.show_active()]["vrf_coordinator"]

    cryptoRoulette = CryptoRoulette.deploy(
        subscription_id,
        vrf_coordinator,
        key_hash,
        {"from": account},
        publish_source=False,
    )
    print("Deployed CryptoRoulette!")
    return cryptoRoulette


def test_dealer_start_end_game_success():
    # everything should work
    account = get_account()
    cryptoRoulette = deploy()
    newGameKey = "mynewgamekey"  # needs to be changed each run on same contract
    ante = Web3.toWei(0.01, "ether")
    cryptoRoulette.startNewGame(ante, newGameKey, {"from": account, "value": ante})
    games = cryptoRoulette.getGames(True)
    print("games")
    print(games)
    dealerGameStatus = cryptoRoulette.getGameStatus(newGameKey)
    print("dealerGameStatus")
    print(dealerGameStatus)
    cryptoRoulette.endGame({"from": account})
    games = cryptoRoulette.getGames(True)
    print("games")
    print(games)
    if games == tuple():
        print("empty tuple")
    dealerGameStatus = cryptoRoulette.getGameStatus(newGameKey)
    print(dealerGameStatus)


def main():
    test_dealer_start_end_game_success()
