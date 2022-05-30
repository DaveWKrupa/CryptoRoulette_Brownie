from brownie import (
    accounts,
    config,
    network,
)


DECIMALS = 8
STARTING_PRICE = 200000000000
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev", "mainnet-fork-infura"]


def get_account(index=None, id=None, configkey=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if configkey:
        return accounts.add(config["wallets"][configkey])
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["private_key_player1"])
