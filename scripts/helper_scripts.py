from brownie import (
    accounts,
    config,
    network,
    Contract,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    interface,
)


DECIMALS = 8
STARTING_PRICE = 200000000000
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev", "mainnet-fork-infura"]

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}  # map name to contract type


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
    return accounts.add(config["wallets"]["from_key"])


# print(f"The active network is {network.show_active()}")
# print("Deploying mocks...")
# MockV3Aggregator is an array of already deployed MockV3Aggregators, so if
# it has not yet been deployed then length of the array = 0
def deploy_mocks(decimals=DECIMALS, initial_value=STARTING_PRICE):
    account = get_account()
    if len(MockV3Aggregator) <= 0:
        MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    if len(LinkToken) <= 0:
        link_token = LinkToken.deploy({"from": account})
    else:
        link_token = LinkToken[-1]
    if len(VRFCoordinatorMock) <= 0:
        VRFCoordinatorMock.deploy(link_token.address, {"from": account})


def get_contract(contract_name):
    """This function will grab the contract address for the named contract from the brownie config if defined,
    otherwise it will deploy a mock version of that contract and return that mock contract.
    Only used for contracts requiring a mock

        Agrs:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: the most recently deployed version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


# fund with link token using the LinkToken.transfer function
def fund_with_link_one(
    contract_address, account=None, link_token=None, amount=100000000000000000
):
    accounttouse = account if account else get_account()
    linktokentouse = link_token if link_token else get_contract("link_token")
    tx = linktokentouse.transfer(contract_address, amount, {"from": accounttouse})
    tx.wait(1)
    print("Fund contract!")


# fund with link token using the LinkToken interface
def fund_with_link_two(
    contract_address, account=None, link_token=None, amount=100000000000000000
):
    accounttouse = account if account else get_account()
    link_token_contract = interface.LinkTokenInterface(link_token.address)
    tx = link_token_contract.transfer(contract_address, amount, {"from": accounttouse})
    tx.wait(1)
    print("Fund contract!")
