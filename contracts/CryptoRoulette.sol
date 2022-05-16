// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract CryptoRoulette is Ownable, VRFConsumerBase {
    ///event declarations
    event gameMessageSent(
        address indexed dealer,
        string gameKey,
        string messageType,
        string message,
        uint256 timeStamp
    );

    event newGameStarted(
        address indexed dealer,
        string gameKey,
        uint256 timeStamp,
        uint256 ante
    );

    event gameEnded(address indexed dealer, string gameKey, uint256 timeStamp);

    event playerJoined(
        address indexed player,
        string gameKey,
        uint256 timeStamp
    );
    /////////////////////////////////////////////////////

    ///enum declarations
    enum GameStatus {
        WAITING_FOR_PLAYERS,
        IN_PROGRESS,
        ENDED
    }
    /////////////////////////////////////////////////////

    ///struct definitions
    struct Player {
        address playerAddress;
        uint256 stackAmount;
    }

    struct DealerGame {
        address dealer;
        uint256 startTime;
        uint256 endTime;
        string gameKey;
        uint256 ante;
        GameStatus gameStatus;
        uint256 potAmount;
        address[6] players;
        uint256[6] playerStacks;
        uint256 playerCount;
    }

    /////////////////////////////////////////////////////

    ///////////////////////////////////

    ///Game data
    string[] internal currentGames; //list of gameKeys for games not ended
    string[] internal gameKeys; //list of all gameKeys used
    mapping(address => string[]) internal dealerGameKeys; //all game keys for dealer
    mapping(string => DealerGame) internal gameKeyDealerGame; //list of all games

    /////////////////////////////////////////////////////

    ///public variables
    //not sure if these need to be public
    address public VRFCoordinator;
    address public LinkToken;

    uint256 public randomnumber; //just for testing
    /////////////////////////////////////////////////////

    ///private variables
    uint256 private dealerFee = ONE_ONEHUNDREDTH_ETH;
    bool private allowNewGames = true;
    bytes32 private keyHash;
    uint256 private linkFee;
    /////////////////////////////////////////////////////

    ///constants
    uint256 private constant ONE_ONETHOUSANDTH_ETH = 1000000000000000;
    uint256 private constant ONE_ONEHUNDREDTH_ETH = 10000000000000000;
    uint256 private constant ONE_TENTH_ETH = 100000000000000000;
    address private constant NULL_ADDRESS =
        0x0000000000000000000000000000000000000000;

    /////////////////////////////////////////////////////

    ///constructor
    constructor(
        address _vrfCoordinator,
        address _linkToken,
        uint256 _linkFee,
        bytes32 _keyHash
    ) VRFConsumerBase(_vrfCoordinator, _linkToken) {
        keyHash = _keyHash;
        linkFee = _linkFee;
        VRFCoordinator = _vrfCoordinator;
        LinkToken = _linkToken;
    }

    /////////////////////////////////////////////////////

    ///Game functions
    function startNewGame(uint256 _ante, string memory _gameKey)
        public
        payable
    {
        (bool success, string memory message) = checkNewGameRequirements(
            msg.sender,
            msg.value,
            _gameKey,
            _ante
        );
        require(success, message);

        uint256 noMoney = 0;

        DealerGame memory dealerGame = DealerGame(
            msg.sender,
            block.timestamp,
            0,
            _gameKey,
            _ante,
            GameStatus.WAITING_FOR_PLAYERS,
            0,
            [
                NULL_ADDRESS,
                NULL_ADDRESS,
                NULL_ADDRESS,
                NULL_ADDRESS,
                NULL_ADDRESS,
                NULL_ADDRESS
            ],
            [noMoney, noMoney, noMoney, noMoney, noMoney, noMoney],
            0
        );

        //The gameKeyDealer mapping and gameKeys array will
        //permanently store this data for future reference
        gameKeyDealerGame[_gameKey] = dealerGame;
        gameKeys.push(_gameKey);
        //the currentGames array only holds gameKeys for games not ended
        currentGames.push(_gameKey);
        //need to have easy access to all gamekeys associated with a dealer
        //so add it to the array in the mapping
        dealerGameKeys[msg.sender].push(_gameKey);
    }

    function endGame() public {
        //Dealer can end the game before the 10 rounds have been finished.
        //They may need to do this if players in the game are
        //unable to submit their numbers. If that is the case then
        //the dealer cannot spin the wheel, so only option is end game.
        //When game is ended prematurely players retain their stack and split the pot.
        (uint256 index, string memory gameKey) = getDealerCurrentGame(
            msg.sender
        );
        require(!isSameString(gameKey, ""), "No current game found.");
        //remove the game from the currentGames array
        removeItemFromCurrentGamesArray(index);
        //set the status = ENDED
        uint256 endTime = block.timestamp;
        gameKeyDealerGame[gameKey].gameStatus = GameStatus.ENDED;
        gameKeyDealerGame[gameKey].endTime = endTime;

        emit gameEnded(msg.sender, gameKey, endTime);
    }

    function joinGame(string memory gameKey) public payable {
        (bool success, string memory message) = checkJoinPlayerRequirements(
            gameKey,
            msg.sender,
            msg.value
        );
        require(success, message);
        bool playerAdded = false;
        // can be up to 6 players per game
        for (uint256 i = 0; i < 6; i++) {
            if (gameKeyDealerGame[gameKey].players[i] == NULL_ADDRESS) {
                //found an empty slot for the player
                gameKeyDealerGame[gameKey].players[i] = msg.sender;
                gameKeyDealerGame[gameKey].playerStacks[i] = msg.value;
                gameKeyDealerGame[gameKey].playerCount += 1;
                playerAdded = true;
                break;
            }
        }
        require(playerAdded, "Game already has 6 players");

        emit playerJoined(msg.sender, gameKey, block.timestamp);
    }

    // function submitNumbers(
    //     address dealer,
    //     uint8 highLow,
    //     uint8 oddEven,
    //     uint8[] memory numbers
    // ) public {
    //     //players get to choose between high or low
    //     //0 = low, non-0 = high
    //     //0 = even, non-0 = odd
    //     //players then get to choose 10 numbers between 1 and 36
    //     //submitted numbers outside that range or duplicates
    //     //result in a wasted pick.
    // }

    // function spinWheel() public {
    //     //forceSpin can be used by dealer when a player is unable to
    //     //submit their numbers for some reason. It allows the game to continue
    //     //with whatever remaining players there are.
    //     require(
    //         checkPlayersSubmitChoices(msg.sender),
    //         "Not all players have submitted their numbers."
    //     );
    //     bytes32 requestId = requestRandomness(keyHash, linkFee);
    //     //emit RequestedRandomness(requestId);
    // }

    function withdrawalStack(address dealer) public payable {
        // require(checkGameStatus(dealer), "Game still in progress.");
    }

    /////////////////////////////////////////////////////

    ///Public helper functions
    function getDealerFee() public view returns (uint256) {
        return dealerFee;
    }

    function getPlayerFee(string memory gameKey) public view returns (uint256) {
        //The players fee is the ante passed in by the dealer when they
        //started the game, times 10. One ante for each of the 10 rounds.
        return gameKeyDealerGame[gameKey].ante * 10;
    }

    function getGames(bool currentOnly) public view returns (string[] memory) {
        if (currentOnly) {
            return currentGames;
        } else {
            return gameKeys;
        }
    }

    function getGameStatus(string memory gameKey)
        public
        view
        returns (string memory)
    {
        if (isGameKeyInUse(gameKey)) {
            if (
                gameKeyDealerGame[gameKey].gameStatus ==
                GameStatus.WAITING_FOR_PLAYERS
            ) {
                return "Waiting for players";
            } else if (
                gameKeyDealerGame[gameKey].gameStatus == GameStatus.IN_PROGRESS
            ) {
                return "In progress";
            } else {
                return "Game ended";
            }
        } else {
            return "Game not found.";
        }
    }

    function getGamePlayers(string memory gameKey)
        public
        view
        returns (
            address[6] memory playerAddresses,
            uint256[6] memory playerStacks
        )
    {
        return (
            gameKeyDealerGame[gameKey].players,
            gameKeyDealerGame[gameKey].playerStacks
        );
    }

    function getDealerGameKeys(address dealer)
        public
        view
        returns (string[] memory keys)
    {
        return dealerGameKeys[dealer];
    }

    function getGameInfo(string memory gameKey)
        public
        view
        returns (
            address dealer,
            uint256 startTime,
            uint256 endTime,
            uint256 ante,
            string memory gameStatus,
            uint256 potAmount,
            uint256 playerCount
        )
    {
        string memory status;
        if (
            gameKeyDealerGame[gameKey].gameStatus ==
            GameStatus.WAITING_FOR_PLAYERS
        ) {
            status = "Waiting for players";
        } else if (
            gameKeyDealerGame[gameKey].gameStatus == GameStatus.IN_PROGRESS
        ) {
            status = "In progress";
        } else {
            status = "Game has ended";
        }
        return (
            gameKeyDealerGame[gameKey].dealer,
            gameKeyDealerGame[gameKey].startTime,
            gameKeyDealerGame[gameKey].endTime,
            gameKeyDealerGame[gameKey].ante,
            status,
            gameKeyDealerGame[gameKey].potAmount,
            gameKeyDealerGame[gameKey].playerCount
        );
    }

    // struct DealerGame {
    //         address dealer;
    //         uint256 startTime;
    //         uint256 endTime;
    //         string gameKey;
    //         uint256 ante;
    //         GameStatus gameStatus;
    //         uint256 potAmount;
    //     }
    //     ////////////////////////////////////////////////////

    ///Internal helper functions
    function getDealerCurrentGame(address dealer)
        internal
        returns (uint256 index, string memory gameKey)
    {
        string[] memory keys = dealerGameKeys[dealer]; //get the gameKeys for the dealer
        if (keys.length == 0) {
            //no games so no current game
            return (0, "");
        }
        string memory latestGameKey = keys[keys.length - 1];
        for (uint256 i = 0; i < currentGames.length; i++) {
            if (isSameString(currentGames[i], latestGameKey)) {
                return (i, latestGameKey); //return the index and the key
            }
        }
        //no current game found
        return (0, "");
    }

    function checkPlayersSubmitChoices(address dealer) internal returns (bool) {
        //Check to make sure all the players have submitted their numbers
        //for this round.
        return true;
    }

    function removeItemFromCurrentGamesArray(uint256 index) internal {
        //the easiest way to remove an item from the array
        //is to copy the last item in the array over the
        //item to be deleted, then popping the last item off
        require(index < currentGames.length);
        currentGames[index] = currentGames[currentGames.length - 1];
        currentGames.pop();
    }

    function isGameKeyInUse(string memory gameKey)
        internal
        view
        returns (bool)
    {
        //gameKey is in use if it has a non-null address in the gameKeyDealer mapping
        return
            gameKeyDealerGame[gameKey].dealer !=
            0x0000000000000000000000000000000000000000;
    }

    function checkNewGameRequirements(
        address _dealer,
        uint256 _dealerPayment,
        string memory _gameKey,
        uint256 _ante
    ) internal returns (bool success, string memory message) {
        if (!allowNewGames) {
            return (
                false,
                "New games not allowed at this time. Check back later."
            );
        }

        if (_dealerPayment < dealerFee) {
            return (false, "Not enough ETH!!!");
        }

        // The ante can be .001 eth, .01 eth or .1 eth
        if (
            _ante != ONE_ONETHOUSANDTH_ETH &&
            _ante != ONE_ONEHUNDREDTH_ETH &&
            _ante != ONE_TENTH_ETH
        ) {
            return (false, "Ante not a valid value.");
        }

        (uint256 index, string memory currentGameKey) = getDealerCurrentGame(
            _dealer
        );
        if (!isSameString(currentGameKey, "")) {
            return (false, "You already have a game in progress.");
        }

        if (isGameKeyInUse(_gameKey)) {
            return (false, "GameKey already in use.");
        }

        return (true, "All conditions satisfied.");
    }

    function checkJoinPlayerRequirements(
        string memory gameKey,
        address player,
        uint256 fee
    ) internal returns (bool success, string memory message) {
        if (fee < gameKeyDealerGame[gameKey].ante * 10) {
            return (false, "Not enough ETH!");
        }
        string memory status = getGameStatus(gameKey);
        if (isSameString(status, "Game not found")) {
            return (false, status);
        }
        if (!isSameString(status, "Waiting for players")) {
            return (false, "Cannot join game at this time.");
        }
        return (true, "");
    }

    function isSameString(string memory string1, string memory string2)
        internal
        returns (bool)
    {
        //Comparing strings in Solidity doesn't work normally
        //TypeError: Operator != not compatible with types string memory and literal_string ""
        //So need to jump some hoops.
        return (keccak256(abi.encodePacked(string1)) ==
            keccak256(abi.encodePacked(string2)));
    }

    ////////////////////////////////////////////////////

    // ///Administrative functions
    // function withdrawal() public payable onlyOwner {
    //     //This is used to withdraw profits from the contract.
    //     //This should not withdraw any eth owned by players.
    // }

    // function setDealerFee(uint256 _newDealerFee) public onlyOwner {
    //     dealerFee = _newDealerFee;
    // }

    // function setAllowNewGames(bool _allowNewGames) public onlyOwner {
    //     allowNewGames = _allowNewGames;
    // }

    // function clearActiveGames() public onlyOwner {
    //     //This allows the owner to set all games to completed
    //     //should there be any active games.
    //     //To be used before owner withdraws eth from the contract.
    //     allowNewGames = false;
    // }

    // // function checkStaleGames(uint265 _hours)
    // //     public
    // //     onlyOwner
    // //     returns (address[] memory)
    // // {
    // //     //Find out if there are any current games that were started
    // //     //longer than _hours ago.
    // //     return address[];
    // // }

    // function sendGameMessage(
    //     address _dealer,
    //     string memory _gameKey,
    //     string memory _message,
    //     uint256 timeStamp
    // ) public onlyOwner {
    //     //emit gameMessageSent(_dealer, "admin", _message);
    // }

    // function forceEndGame(address _dealer, string memory _message)
    //     public
    //     onlyOwner
    // {
    //     //To be used for abandoned games or other situations
    //     //where a game cannot be completed by the dealer.
    //     //emit gameMessageSent(_dealer, "admin", _message);
    // }

    // function setLinkFee(uint256 _linkFee) public onlyOwner {
    //     linkFee = _linkFee;
    // }

    ////////////////////////////////////////////////////

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        //emit RandomnessReceived(_randomness);
        // require(
        //     lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
        //     "Lottery is not calculating winner."
        // );
        // require(
        //     _randomness > 0,
        //     "Random number not returned by VRFConsumerBase"
        // );
        randomnumber = _randomness;
    }
}
