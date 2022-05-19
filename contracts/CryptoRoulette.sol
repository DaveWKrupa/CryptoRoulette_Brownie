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

    event playerSubmittedNumbers(
        address indexed player,
        string gameKey,
        uint256 timeStamp,
        uint256 highLow,
        uint256 oddEven,
        uint256[] numbers
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

    struct DealerGame {
        address dealer;
        uint256 startTime;
        uint256 endTime;
        string gameKey;
        uint256 ante;
        GameStatus gameStatus;
        uint256 potAmount;
        bool submitLocked;
        address[6] players;
        uint256[6] playerStacks;
        uint256 playerCount;
        uint256 currentRound;
    }

    /////////////////////////////////////////////////////

    ///////////////////////////////////

    ///Game data
    string[] internal currentGames; //list of gameKeys for games not ended
    string[] internal gameKeys; //list of all gameKeys used
    mapping(address => string[]) internal dealerGameKeys; //all game keys for dealer
    mapping(string => DealerGame) internal gameKeyDealerGame; //list of all games

    //Need to keep track of submitted numbers by players
    //The parent mapping uses the gameKey as the key
    //The mapping will be reset for every round in a game

    //highLowPlayers mapping holds the choices in a round for the high/low bets
    //players who choose "low numbers (1 - 18) will have their
    //addresses stored in the array with 0 as the key
    //players who choose "high numbers (19 - 36) will have their
    //addresses stored in the array with 1 as the key
    mapping(string => mapping(uint256 => address[])) internal highLowPlayers;

    //oddEvenPlayers mapping holds the choices in a round for the odd/even bets
    //players who choose "odd numbers will have their
    //addresses stored in the array with 0 as the key
    //players who choose "even numbers will have their
    //addresses stored in the array with 1 as the key
    mapping(string => mapping(uint256 => address[])) internal oddEvenPlayers;

    //numberPickPlayers mapping holds the choices in a round for the numbers bets
    //for each game round there is a mapping with keys 1 - 36
    //the address array will hold all players who picked the
    //number corresponding to the key
    mapping(string => mapping(uint256 => address[])) internal numberPickPlayers;

    //the three mappings above used to efficiently find winners
    //but they are not good for efficiently returning
    //a player's choices. So a fourth mapping will hold
    //an array of the player's choices
    mapping(string => mapping(address => uint256[12])) internal playersPicks;

    /////////////////////////////////////////////////////

    ///public variables
    //not sure if these need to be public
    address public VRFCoordinator;
    address public LinkToken;

    uint256 public randomnumber; //just for testing
    /////////////////////////////////////////////////////

    ///private variables
    uint256 private cryptoRouletteBank = 0; //keep track of dealer fees added
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
    uint256 private constant HIGHLOW_HIGH = 0;
    uint256 private constant HIGHLOW_LOW = 1;
    uint256 private constant ODDEVEN_ODD = 0;
    uint256 private constant ODDEVEN_EVEN = 1;

    string private constant WAITING_FOR_PLAYERS_STRING = "Waiting for players";
    string private constant IN_PROGRESS_STRING = "In progress";
    string private constant GAME_ENDED_STRING = "Game ended";
    string private constant GAME_NOT_FOUND_STRING = "Game not found";

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

        //dealer pays a fee to start a game
        //keep track of the dealer fees added to the contract
        cryptoRouletteBank += msg.value;

        uint256 noMoney = 0;

        DealerGame memory dealerGame = DealerGame(
            msg.sender,
            block.timestamp,
            0,
            _gameKey,
            _ante,
            GameStatus.WAITING_FOR_PLAYERS,
            0,
            false,
            [
                NULL_ADDRESS,
                NULL_ADDRESS,
                NULL_ADDRESS,
                NULL_ADDRESS,
                NULL_ADDRESS,
                NULL_ADDRESS
            ],
            [noMoney, noMoney, noMoney, noMoney, noMoney, noMoney],
            0,
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

    function setGameToInProgress(string memory gameKey) public {
        (uint256 index, string memory gameKey2) = getDealerCurrentGame(
            msg.sender
        );
        require(!isSameString(gameKey2, ""), GAME_NOT_FOUND_STRING);
        require(
            isSameString(gameKey2, gameKey),
            "Game key is not current game for dealer."
        );
        require(
            gameKeyDealerGame[gameKey].gameStatus ==
                GameStatus.WAITING_FOR_PLAYERS,
            "Game already in progress or ended."
        );
        gameKeyDealerGame[gameKey].gameStatus = GameStatus.IN_PROGRESS;
        gameKeyDealerGame[gameKey].currentRound = 1;
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
        require(!isSameString(gameKey, ""), GAME_NOT_FOUND_STRING);
        //remove the game from the currentGames array
        removeItemFromCurrentGamesArray(index);
        //set the status = ENDED
        uint256 endTime = block.timestamp;
        gameKeyDealerGame[gameKey].gameStatus = GameStatus.ENDED;
        gameKeyDealerGame[gameKey].endTime = endTime;

        if (gameKeyDealerGame[gameKey].potAmount > 0) {
            //if there is money still in the pot then
            //split it evenly between the players
            uint256 playerCut = gameKeyDealerGame[gameKey].potAmount /
                gameKeyDealerGame[gameKey].playerCount;

            for (
                uint256 i = 0;
                i < gameKeyDealerGame[gameKey].playerCount;
                i++
            ) {
                gameKeyDealerGame[gameKey].playerStacks[i] += playerCut;
            }
        }

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

    function submitNumbers(
        string memory gameKey,
        uint256 highLow,
        uint256 oddEven,
        uint256[] memory numbers
    ) public {
        require(playerIsInGame(gameKey, msg.sender), "Player not in game.");
        require(
            gameKeyDealerGame[gameKey].gameStatus == GameStatus.IN_PROGRESS,
            "Cannot submit numbers. Game is not in progress."
        );
        require(
            !hasPlayerSubmittedNumbers(gameKey, msg.sender),
            "Player already submitted numbers."
        );
        require(
            !gameKeyDealerGame[gameKey].submitLocked,
            "Too many players submitting at one time. Please try again."
        );

        //make sure only one player submits at a time
        //to avoid collision updating potAmount
        gameKeyDealerGame[gameKey].submitLocked = true;

        //the highLowPlayers, oddEvenPlayers and numberPickPlayers
        //are made to efficiently identify winners without a lot of looping.
        //But these mappings are not good for retrieving a specific
        //player's picks, so need to save off the player's picks
        // in an easy to access mapping playersPicks

        if (highLow == HIGHLOW_HIGH) {
            highLowPlayers[gameKey][HIGHLOW_HIGH].push(msg.sender);
            playersPicks[gameKey][msg.sender][0] = HIGHLOW_HIGH;
        } else {
            highLowPlayers[gameKey][HIGHLOW_LOW].push(msg.sender);
            playersPicks[gameKey][msg.sender][0] = HIGHLOW_LOW;
        }
        if (oddEven == ODDEVEN_ODD) {
            oddEvenPlayers[gameKey][ODDEVEN_ODD].push(msg.sender);
            playersPicks[gameKey][msg.sender][1] = ODDEVEN_ODD;
        } else {
            oddEvenPlayers[gameKey][ODDEVEN_EVEN].push(msg.sender);
            playersPicks[gameKey][msg.sender][1] = ODDEVEN_EVEN;
        }
        uint256 numbersCount = numbers.length;
        //player gets up to 10 choices for individual numbers
        if (numbersCount > 10) {
            numbersCount = 10;
        }
        //players get to choose 10 numbers between 1 and 36
        //submitted numbers outside that range
        //result in a wasted pick.
        for (uint256 i = 0; i < numbersCount; i++) {
            //loop through the numbers and add the players address to the mapping
            //where the key is the chosen number
            numberPickPlayers[gameKey][numbers[i]].push(msg.sender);
            playersPicks[gameKey][msg.sender][i + 2] = numbers[i];
        }

        //subtract the ante from the player's stack
        //and add it to the pot
        for (uint256 i = 0; i < gameKeyDealerGame[gameKey].playerCount; i++) {
            if (gameKeyDealerGame[gameKey].players[i] == msg.sender) {
                gameKeyDealerGame[gameKey].playerStacks[i] -= gameKeyDealerGame[
                    gameKey
                ].ante;
                gameKeyDealerGame[gameKey].potAmount += gameKeyDealerGame[
                    gameKey
                ].ante;
                break;
            }
        }
        //we can now allow other players to submit their numbers
        gameKeyDealerGame[gameKey].submitLocked = false;

        emit playerSubmittedNumbers(
            msg.sender,
            gameKey,
            block.timestamp,
            highLow,
            oddEven,
            numbers
        );
    }

    function spinWheel(string memory gameKey) public {
        require(
            msg.sender == gameKeyDealerGame[gameKey].dealer,
            "Only dealer can spin wheel."
        );
        require(
            (highLowPlayers[gameKey][HIGHLOW_HIGH].length +
                highLowPlayers[gameKey][HIGHLOW_LOW].length) ==
                gameKeyDealerGame[gameKey].playerCount,
            "Not all players have submitted numbers."
        );
        // require(
        //     checkPlayersSubmitChoices(msg.sender),
        //     "Not all players have submitted their numbers."
        // );
        // bytes32 requestId = requestRandomness(keyHash, linkFee);
        //emit RequestedRandomness(requestId);
    }

    function withdrawalStack(string memory gameKey) public payable {
        require(
            gameKeyDealerGame[gameKey].gameStatus == GameStatus.ENDED,
            "Game still in progress."
        );
        uint256 balanceOwed = 0;
        //find the player's stack in the game and set balanceOwed
        //if player not found in game then throw error
        for (uint256 i = 0; i < gameKeyDealerGame[gameKey].playerCount; i++) {
            if (gameKeyDealerGame[gameKey].players[i] == msg.sender) {
                balanceOwed = gameKeyDealerGame[gameKey].playerStacks[i];
                //to avoid a re-entrancy attack
                //set the playerStack to 0 before transferring the funds
                gameKeyDealerGame[gameKey].playerStacks[i] = 0;
                break;
            }
        }
        require(balanceOwed > 0, "You have no money in this game.");
        payable(msg.sender).transfer(balanceOwed);
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
                return WAITING_FOR_PLAYERS_STRING;
            } else if (
                gameKeyDealerGame[gameKey].gameStatus == GameStatus.IN_PROGRESS
            ) {
                return IN_PROGRESS_STRING;
            } else {
                return GAME_ENDED_STRING;
            }
        } else {
            return GAME_NOT_FOUND_STRING;
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
            uint256 ante,
            string memory gameStatus,
            uint256 potAmount,
            uint256 playerCount,
            uint256 currentRound
        )
    {
        string memory status;
        if (
            gameKeyDealerGame[gameKey].gameStatus ==
            GameStatus.WAITING_FOR_PLAYERS
        ) {
            status = WAITING_FOR_PLAYERS_STRING;
        } else if (
            gameKeyDealerGame[gameKey].gameStatus == GameStatus.IN_PROGRESS
        ) {
            status = IN_PROGRESS_STRING;
        } else {
            status = GAME_ENDED_STRING;
        }
        return (
            gameKeyDealerGame[gameKey].dealer,
            gameKeyDealerGame[gameKey].ante,
            status,
            gameKeyDealerGame[gameKey].potAmount,
            gameKeyDealerGame[gameKey].playerCount,
            gameKeyDealerGame[gameKey].currentRound
        );
    }

    function getPlayerPicks(string memory gameKey, address player)
        public
        view
        returns (uint256 round, uint256[12] memory)
    {
        return (
            gameKeyDealerGame[gameKey].currentRound,
            playersPicks[gameKey][player]
        );
    }

    //////////////////////////////////////////////////////

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
        //the easiest way to remove an item from the array in Solidity
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
        if (isSameString(status, GAME_NOT_FOUND_STRING)) {
            return (false, status);
        }
        if (!isSameString(status, WAITING_FOR_PLAYERS_STRING)) {
            return (false, "Cannot join game at this time.");
        }
        if (playerIsInGame(gameKey, player)) {
            return (false, "Player already in game.");
        }
        return (true, "");
    }

    function playerIsInGame(string memory gameKey, address player)
        internal
        returns (bool)
    {
        for (uint256 i = 0; i < gameKeyDealerGame[gameKey].playerCount; i++) {
            if (gameKeyDealerGame[gameKey].players[i] == msg.sender) {
                return true;
            }
        }
        return false;
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

    function hasPlayerSubmittedNumbers(string memory gameKey, address player)
        internal
        returns (bool)
    {
        address[] memory playersHigh = highLowPlayers[gameKey][0];
        for (uint256 i = 1; i < playersHigh.length; i++) {
            if (playersHigh[i] == player) {
                return true;
            }
        }
        address[] memory playersLow = highLowPlayers[gameKey][0];
        for (uint256 i = 1; i < playersLow.length; i++) {
            if (playersLow[i] == player) {
                return true;
            }
        }
        return false;
    }

    function clearGameNumbers(string memory gameKey) internal {
        address[] memory emptyAddressArray;
        //mapping(string => mapping(uint256 => address[])) internal highLowPlayers;
        highLowPlayers[gameKey][0] = emptyAddressArray;
        highLowPlayers[gameKey][1] = emptyAddressArray;

        //mapping(string => mapping(uint256 => address[])) internal oddEvenPlayers;
        oddEvenPlayers[gameKey][0] = emptyAddressArray;
        oddEvenPlayers[gameKey][1] = emptyAddressArray;
        //mapping(string => mapping(uint256 => address[])) internal numberPickPlayers;
        for (uint256 i = 1; i < 37; i++) {
            numberPickPlayers[gameKey][i] = emptyAddressArray;
        }
    }

    ////////////////////////////////////////////////////

    // ///Administrative functions
    function getCryptoRouletteBalance()
        public
        view
        onlyOwner
        returns (uint256)
    {
        return address(this).balance;
    }

    function getDealerFeeBalance() public view onlyOwner returns (uint256) {
        return cryptoRouletteBank;
    }

    function withdrawDealerFees() public payable onlyOwner {
        //This is used to withdraw dealer fees from the contract.
        //This should not withdraw any eth owned by players.
        uint256 amountToWithdraw = cryptoRouletteBank;
        cryptoRouletteBank = 0; //zero out the amount before transfer
        payable(msg.sender).transfer(amountToWithdraw);
    }

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

    function setLinkFee(uint256 _linkFee) public onlyOwner {
        linkFee = _linkFee;
    }

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
