// SPDX-License-Identifier: MIT

pragma solidity ^0.8.8;

import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract RandomNumber is Ownable, VRFConsumerBaseV2 {
    event randomNumbersReturned(
        string indexed requestKeyHash,
        string requestKey,
        uint256 timeStamp
    );

    VRFCoordinatorV2Interface private immutable COORDINATOR;

    // VRF coordinator
    uint64 private immutable s_subscriptionId;
    bytes32 private immutable s_keyHash;

    uint32 private constant callbackGasLimit = 500000;
    uint16 private constant requestConfirmations = 3;

    mapping(uint256 => string) private requestIDRequestKey;
    mapping(string => uint256[]) private requestKeyRandomNumbers;
    mapping(address => bool) private whitelist; //addresses that can use this contract

    constructor(
        uint64 _subscriptionId,
        address _vrfCoordinator,
        bytes32 _keyHash
    ) VRFConsumerBaseV2(_vrfCoordinator) {
        COORDINATOR = VRFCoordinatorV2Interface(_vrfCoordinator);
        s_subscriptionId = _subscriptionId;
        s_keyHash = _keyHash;
        whitelist[msg.sender] = true;
    }

    function requestRandomNumbers(
        string memory requestKey,
        uint32 numberRequested
    ) external {
        require(whitelist[msg.sender], "Invalid caller");

        if (numberRequested > 10) {
            numberRequested = 10;
        }
        uint256 requestId = COORDINATOR.requestRandomWords(
            s_keyHash,
            s_subscriptionId,
            requestConfirmations,
            callbackGasLimit,
            numberRequested
        );
        requestIDRequestKey[requestId] = requestKey;
    }

    function retrieveRandomNumbers(string memory requestKey)
        external
        view
        returns (uint256[] memory)
    {
        require(whitelist[msg.sender], "Invalid caller");

        return requestKeyRandomNumbers[requestKey];
    }

    //This is the callback for the VRF Coordinator to return
    //an array of random numbers.
    function fulfillRandomWords(
        uint256 _requestId,
        uint256[] memory _randomWords
    ) internal override {
        string memory requestKey = requestIDRequestKey[_requestId];
        requestKeyRandomNumbers[requestKey] = _randomWords;
        emit randomNumbersReturned(requestKey, requestKey, block.timestamp);
    }

    function setWhitelistAddress(address caller, bool allow)
        external
        onlyOwner
    {
        whitelist[caller] = allow;
    }
}
