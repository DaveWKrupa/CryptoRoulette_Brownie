from brownie import RandomNumber, network, config
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

    randomNumber = RandomNumber.deploy(
        subscription_id,
        vrf_coordinator,
        key_hash,
        {"from": account},
        publish_source=False,
    )
    print("Deployed RandomNumber!")
    return randomNumber
