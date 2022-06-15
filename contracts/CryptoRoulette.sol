// SPDX-License-Identifier: MIT

pragma solidity ^0.8.7;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

interface IRandomNumber {
    function requestRandomNumbers(
        string memory requestKey,
        uint32 numberRequested
    ) external;

    function retrieveRandomNumbers(string memory requestKey)
        external
        view
        returns (uint256[] memory);
}

contract CryptoRoulette is Ownable {
    bool CHAINLINK_NOT_WORKING = true;

    address s_randomNumberContract;

    constructor(address randomNumberContract) {
        s_randomNumberContract = randomNumberContract;
    }

    ///event declarations

    //indexed strings are hashed to allow the search to work
    //so also include a readable string gameKey
    //without the indexed modifier
    event newGameStarted(
        address indexed dealer,
        string indexed gameKeyHash,
        string gameKey,
        uint256 timeStamp,
        uint256 ante
    );

    event gameStatusChanged(
        address indexed dealer,
        string indexed gameKeyHash,
        string gameKey,
        uint256 timeStamp,
        string newStatus
    );

    event playerJoined(
        address indexed player,
        string indexed gameKeyHash,
        string gameKey,
        uint256 timeStamp
    );

    event playerSubmittedNumbers(
        address indexed player,
        string indexed gameKeyHash,
        string gameKey,
        uint256 timeStamp,
        uint256 highLow,
        uint256 oddEven,
        uint256[10] numbers,
        uint256 ante,
        uint256 playersStack
    );

    event rouletteWheelSpun(
        string indexed gameKeyHash,
        string gameKey,
        uint256 timeStamp,
        uint256 currentRound,
        uint256 winningNumber
    );

    event playerWon(
        address indexed player,
        string indexed gameKeyHash,
        string gameKey,
        string playerName,
        string category,
        uint256 amountWon,
        uint256 playerStack,
        uint256 currentRound
    );

    event randomNumberRequestReturn(
        string indexed gameKeyHash,
        string gameKey,
        bool succeeded
    );

    /////////////////////////////////////////////////////
    /////////////////////////////////////////////////////
    /////////////////////////////////////////////////////

    ///enum declarations
    enum GameStatus {
        INITIALIZING,
        WAITING_FOR_PLAYERS,
        IN_PROGRESS,
        ENDED
    }
    /////////////////////////////////////////////////////
    /////////////////////////////////////////////////////
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
        bool locked;
        address[6] players;
        uint256[6] playerStacks;
        uint256 playerCount;
        uint256 currentRound;
    }

    /////////////////////////////////////////////////////
    /////////////////////////////////////////////////////
    /////////////////////////////////////////////////////

    ///Game data
    string[] internal currentGames; //list of gameKeys for games not ended
    string[] internal gameKeys; //list of all gameKeys used
    mapping(address => string[]) internal dealerGameKeys; //all game keys for dealer
    mapping(string => DealerGame) internal gameKeyDealerGame; //list of all games
    //Player names passed in from UI when joining game
    mapping(address => string) internal addressPlayerName;
    //used for matching random number requests to the game making the request
    mapping(uint256 => string) internal requestIDGameKey;
    mapping(string => uint256[10]) internal winningNumbers;

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
    //the key will be the gameKey with a dash and the round (e.g. mygamekey-3)
    mapping(string => mapping(address => uint256[12])) internal playersPicks;

    /////////////////////////////////////////////////////
    /////////////////////////////////////////////////////
    /////////////////////////////////////////////////////

    ///private variables

    uint256 private cryptoRouletteBank = 0; //keep track of dealer fees added
    //uint256 private dealerFee = ONE_ONEHUNDREDTH_ETH;
    uint256 private dealerFee = ONE_ONETHOUSANDTH_ETH;
    bool private allowNewGames = true;

    //Can only request one random number
    //from VRFConsumerBaseV2 at a time per contract.
    //So once a request is made, wait until the
    //fulfillRandomWords is called before making new request
    //randomNumberRequestLocked used to block new calls
    bool randomNumberRequestLocked = false;
    //keep track of when the last time the lock was made
    uint256 randomNumberRequestLockTime;
    /////////////////////////////////////////////////////
    /////////////////////////////////////////////////////
    /////////////////////////////////////////////////////

    ///constants
    uint256 private constant ONE_ONETHOUSANDTH_ETH = 1000000000000000;
    uint256 private constant ONE_ONEHUNDREDTH_ETH = 10000000000000000;
    uint256 private constant ONE_TENTH_ETH = 100000000000000000;
    address private constant NULL_ADDRESS =
        0x0000000000000000000000000000000000000000;
    uint256 private constant HIGHLOW_HIGH = 1;
    uint256 private constant HIGHLOW_LOW = 0;
    uint256 private constant ODDEVEN_ODD = 1;
    uint256 private constant ODDEVEN_EVEN = 0;

    string private constant INITIALIZING_STRING = "Game is initializing";
    string private constant WAITING_FOR_PLAYERS_STRING = "Waiting for players";
    string private constant IN_PROGRESS_STRING = "In progress";
    string private constant GAME_ENDED_STRING = "Game ended";
    string private constant GAME_NOT_FOUND_STRING = "Game not found";

    uint256 private constant GAME_TIMEOUT_IN_SECONDS = 3600;

    ///Game functions
    function startNewGame(uint256 _ante, string memory _gameKey)
        external
        payable
    {
        (bool success, string memory message) = checkNewGameRequirements(
            msg.sender,
            msg.value,
            _gameKey,
            _ante
        );

        require(success, message);

        //first make a request for new random numbers using the RandomNumber contract
        IRandomNumber(s_randomNumberContract).requestRandomNumbers(
            _gameKey,
            10
        );

        uint256 timeStamp = block.timestamp;
        //dealer pays a fee to start a game
        //keep track of the dealer fees added to the contract
        cryptoRouletteBank += msg.value;

        DealerGame memory dealerGame = DealerGame(
            msg.sender,
            timeStamp,
            0,
            _gameKey,
            _ante,
            GameStatus.INITIALIZING,
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
            [
                uint256(0),
                uint256(0),
                uint256(0),
                uint256(0),
                uint256(0),
                uint256(0)
            ],
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
        emit newGameStarted(msg.sender, _gameKey, _gameKey, timeStamp, _ante);
        emit gameStatusChanged(
            msg.sender,
            _gameKey,
            _gameKey,
            timeStamp,
            INITIALIZING_STRING
        );
    }

    //The dealer can cancel a new game provided
    //no one has joined the game yet.
    function cancelNewGame(string memory _gameKey) external {
        (bool success, string memory message) = checkCancelNewGame(
            _gameKey,
            msg.sender
        );
        require(success, message);

        if (gameKeyDealerGame[_gameKey].gameStatus == GameStatus.INITIALIZING) {
            //If the game gets stuck in initializing state,
            //refund the dealer fees
            payable(msg.sender).transfer(dealerFee);
        }

        for (uint256 i = 0; i < currentGames.length; i++) {
            if (isSameString(currentGames[i], _gameKey)) {
                removeItemFromCurrentGamesArray(i);
                break;
            }
        }
        gameKeyDealerGame[_gameKey].gameStatus = GameStatus.ENDED;
    }

    //The UI calls this to retrieve
    function setReadyForPlayers(string memory _gameKey) external {
        require(
            gameKeyDealerGame[_gameKey].gameStatus == GameStatus.INITIALIZING,
            "Cannot set game status"
        );
        uint256[] memory randomNumbers = IRandomNumber(s_randomNumberContract)
            .retrieveRandomNumbers(_gameKey);
        require(
            randomNumbers.length > 0,
            "Game not initialized. Try again later."
        );
        storeRandomNumbers(_gameKey, randomNumbers);
        gameKeyDealerGame[_gameKey].gameStatus = GameStatus.WAITING_FOR_PLAYERS;
    }

    //When the dealer is satisfied everyone has joined the game
    //they set the game status to "in progress"
    //so that players can submit their numbers for the first round.
    function setGameToInProgress(string memory _gameKey) external {
        (
            bool success,
            string memory message
        ) = checkSetGameToInProgressRequirements(_gameKey, msg.sender);
        require(success, message);

        gameKeyDealerGame[_gameKey].gameStatus = GameStatus.IN_PROGRESS;
        gameKeyDealerGame[_gameKey].currentRound = 1;
        emit gameStatusChanged(
            msg.sender,
            _gameKey,
            _gameKey,
            block.timestamp,
            IN_PROGRESS_STRING
        );
    }

    //Each player calls this to join a game
    function joinGame(string memory _gameKey, string memory playerName)
        external
        payable
    {
        (bool success, string memory message) = checkJoinPlayerRequirements(
            _gameKey,
            msg.sender,
            msg.value
        );
        require(success, message);

        bool playerAdded = false;
        // can be up to 6 players per game
        for (uint256 i = 0; i < 6; i++) {
            if (gameKeyDealerGame[_gameKey].players[i] == NULL_ADDRESS) {
                //found an empty slot for the player
                gameKeyDealerGame[_gameKey].players[i] = msg.sender;
                gameKeyDealerGame[_gameKey].playerStacks[i] = msg.value;
                gameKeyDealerGame[_gameKey].playerCount += 1;
                playerAdded = true;
                break;
            }
        }
        require(playerAdded, "Game already has 6 players");
        addressPlayerName[msg.sender] = playerName;
        emit playerJoined(msg.sender, _gameKey, _gameKey, block.timestamp);
    }

    //Players call this to submit their numbers each round
    function submitNumbers(
        string memory _gameKey,
        uint256 _highLow,
        uint256 _oddEven,
        uint256[] memory _numbers
    ) external {
        (
            bool player_can_submit,
            string memory message
        ) = checkPlayerSubmitRequirements(_gameKey, msg.sender);

        require(player_can_submit, message);

        //make sure only one player submits at a time
        //to avoid collision updating potAmount
        //if in the future more than one transaction
        //can be run at a time on the blockchain.
        gameKeyDealerGame[_gameKey].locked = true;

        //the highLowPlayers, oddEvenPlayers and numberPickPlayers
        //are made to efficiently identify winners without a lot of looping.
        //But these mappings are not good for retrieving a specific
        //player's picks, so need to save off the player's picks
        //in an easy to access mapping playersPicks

        string memory playersPicksKey = concatenateStrings(
            _gameKey,
            "-",
            Strings.toString(gameKeyDealerGame[_gameKey].currentRound)
        );

        if (_highLow == HIGHLOW_HIGH) {
            highLowPlayers[_gameKey][HIGHLOW_HIGH].push(msg.sender);
            playersPicks[playersPicksKey][msg.sender][0] = HIGHLOW_HIGH;
        } else {
            highLowPlayers[_gameKey][HIGHLOW_LOW].push(msg.sender);
            playersPicks[playersPicksKey][msg.sender][0] = HIGHLOW_LOW;
        }
        if (_oddEven == ODDEVEN_ODD) {
            oddEvenPlayers[_gameKey][ODDEVEN_ODD].push(msg.sender);
            playersPicks[playersPicksKey][msg.sender][1] = ODDEVEN_ODD;
        } else {
            oddEvenPlayers[_gameKey][ODDEVEN_EVEN].push(msg.sender);
            playersPicks[playersPicksKey][msg.sender][1] = ODDEVEN_EVEN;
        }
        uint256 numbersCount = _numbers.length;
        //player gets up to 10 choices for individual numbers
        if (numbersCount > 10) {
            numbersCount = 10;
        }

        //in the event we will want to pass back only valid
        uint256[10] memory validNumbers;
        //players get to choose 10 numbers between 1 and 36
        //submitted numbers outside that range
        //result in a wasted pick.
        for (uint256 i = 0; i < numbersCount; i++) {
            //loop through the numbers and add the players address to the mapping
            //where the key is the chosen number
            numberPickPlayers[_gameKey][_numbers[i]].push(msg.sender);
            playersPicks[playersPicksKey][msg.sender][i + 2] = _numbers[i];
            validNumbers[i] = _numbers[i];
        }

        uint256 playersStack;
        //subtract the ante from the player's stack
        //and add it to the pot
        for (uint256 i = 0; i < gameKeyDealerGame[_gameKey].playerCount; i++) {
            if (gameKeyDealerGame[_gameKey].players[i] == msg.sender) {
                gameKeyDealerGame[_gameKey].playerStacks[
                    i
                ] -= gameKeyDealerGame[_gameKey].ante;
                gameKeyDealerGame[_gameKey].potAmount += gameKeyDealerGame[
                    _gameKey
                ].ante;
                //save the player's new stack for the event
                playersStack = gameKeyDealerGame[_gameKey].playerStacks[i];
                break;
            }
        }
        //we can now allow other players to submit their numbers
        gameKeyDealerGame[_gameKey].locked = false;

        uint256 ante = gameKeyDealerGame[_gameKey].ante;

        emit playerSubmittedNumbers(
            msg.sender,
            _gameKey,
            _gameKey,
            block.timestamp,
            _highLow,
            _oddEven,
            validNumbers,
            ante,
            playersStack
        );

        if (
            (highLowPlayers[_gameKey][HIGHLOW_HIGH].length +
                highLowPlayers[_gameKey][HIGHLOW_LOW].length) ==
            gameKeyDealerGame[_gameKey].playerCount
        ) {
            //all players have submitted numbers, so time to pay the winners
            payWinners(_gameKey, gameKeyDealerGame[_gameKey].currentRound);
        }
    }

    //If the game has ended, or if the game has passed a certain time limit,
    //players call this to collect their ether
    function withdrawalStack(string memory _gameKey) external payable {
        (bool allowWithdrawal, string memory message) = checkAllowWithdrawal(
            _gameKey
        );
        require(allowWithdrawal, message);

        uint256 balanceOwed = 0;
        //find the player's stack in the game and set balanceOwed
        //if player not found in game then throw error
        for (uint256 i = 0; i < gameKeyDealerGame[_gameKey].playerCount; i++) {
            if (gameKeyDealerGame[_gameKey].players[i] == msg.sender) {
                balanceOwed = gameKeyDealerGame[_gameKey].playerStacks[i];
                //to avoid a re-entrancy attack
                //set the playerStack to 0 before transferring the funds
                gameKeyDealerGame[_gameKey].playerStacks[i] = 0;
                break;
            }
        }
        require(balanceOwed > 0, "You have no money in this game.");
        payable(msg.sender).transfer(balanceOwed);
    }

    /////////////////////////////////////////////////////
    /////////////////////////////////////////////////////
    /////////////////////////////////////////////////////

    ///external helper functions
    function getDealerFee() external view returns (uint256) {
        return dealerFee;
    }

    function getPlayerFee(string memory _gameKey)
        external
        view
        returns (uint256)
    {
        //The players fee is the ante passed in by the dealer when they
        //started the game, times 10. One ante for each of the 10 rounds.
        return gameKeyDealerGame[_gameKey].ante * 10;
    }

    function getGames(bool _currentOnly)
        external
        view
        returns (string[] memory)
    {
        if (_currentOnly) {
            return currentGames;
        } else {
            return gameKeys;
        }
    }

    function getGameStatus(string memory _gameKey)
        public
        view
        returns (string memory)
    {
        if (isGameKeyInUse(_gameKey)) {
            if (
                gameKeyDealerGame[_gameKey].gameStatus ==
                GameStatus.INITIALIZING
            ) {
                return INITIALIZING_STRING;
            } else if (
                gameKeyDealerGame[_gameKey].gameStatus ==
                GameStatus.WAITING_FOR_PLAYERS
            ) {
                return WAITING_FOR_PLAYERS_STRING;
            } else if (
                gameKeyDealerGame[_gameKey].gameStatus == GameStatus.IN_PROGRESS
            ) {
                return IN_PROGRESS_STRING;
            } else {
                return GAME_ENDED_STRING;
            }
        } else {
            return GAME_NOT_FOUND_STRING;
        }
    }

    function getGamePlayers(string memory _gameKey)
        external
        view
        returns (
            address[6] memory playerAddresses,
            uint256[6] memory playerStacks
        )
    {
        return (
            gameKeyDealerGame[_gameKey].players,
            gameKeyDealerGame[_gameKey].playerStacks
        );
    }

    function getDealerGameKeys(address _dealer)
        external
        view
        returns (string[] memory keys)
    {
        return dealerGameKeys[_dealer];
    }

    function getGameInfo(string memory _gameKey)
        external
        view
        returns (
            address dealer,
            uint256 ante,
            string memory gameStatus,
            uint256 potAmount,
            uint256 playerCount,
            uint256 currentRound,
            uint256 startTime
        )
    {
        string memory status;
        if (gameKeyDealerGame[_gameKey].gameStatus == GameStatus.INITIALIZING) {
            status = INITIALIZING_STRING;
        } else if (
            gameKeyDealerGame[_gameKey].gameStatus ==
            GameStatus.WAITING_FOR_PLAYERS
        ) {
            status = WAITING_FOR_PLAYERS_STRING;
        } else if (
            gameKeyDealerGame[_gameKey].gameStatus == GameStatus.IN_PROGRESS
        ) {
            status = IN_PROGRESS_STRING;
        } else {
            status = GAME_ENDED_STRING;
        }
        return (
            gameKeyDealerGame[_gameKey].dealer,
            gameKeyDealerGame[_gameKey].ante,
            status,
            gameKeyDealerGame[_gameKey].potAmount,
            gameKeyDealerGame[_gameKey].playerCount,
            gameKeyDealerGame[_gameKey].currentRound,
            gameKeyDealerGame[_gameKey].startTime
        );
    }

    function getPlayerPicks(
        string memory _gameKey,
        uint256 round,
        address _player
    ) external view returns (uint256[12] memory) {
        string memory playersPicksKey = concatenateStrings(
            _gameKey,
            "-",
            Strings.toString(round)
        );
        return playersPicks[playersPicksKey][_player];
    }

    function getWinningNumber(string memory _gameKey, uint256 round)
        external
        view
        returns (uint256)
    {
        if (round < gameKeyDealerGame[_gameKey].currentRound) {
            //can only get winning numbers for rounds already played
            string memory winningNumberKey = concatenateStrings(
                _gameKey,
                "-",
                Strings.toString(round)
            );
            return winningNumbers[winningNumberKey][round - 1];
        } else {
            return 0;
        }
    }

    /////////////////////////////////////////////////////
    /////////////////////////////////////////////////////
    /////////////////////////////////////////////////////

    ///Internal functions
    //The round is done, pay the winners based on the winning number
    function payWinners(string memory _gameKey, uint256 _currentRound)
        internal
    {
        //the winning number is between 1 and 36 inclusive
        uint256 winningNumber = winningNumbers[_gameKey][_currentRound - 1];
        emit rouletteWheelSpun(
            _gameKey,
            _gameKey,
            block.timestamp,
            _currentRound,
            winningNumber
        );

        bool isOdd = (winningNumber % 2 != 0);
        bool isLow = (winningNumber < 18);
        //winners of odd/even and high/low get to split 25% of the pot each
        uint256 quarterPot = gameKeyDealerGame[_gameKey].potAmount / 4;
        //winners of the exact match get to split 50% of the pot
        uint256 halfPot = gameKeyDealerGame[_gameKey].potAmount / 2;
        payOddEvenWinners(_gameKey, isOdd, quarterPot);
        payHighLowWinners(_gameKey, isLow, quarterPot);
        payExactMatchWinners(_gameKey, halfPot, winningNumber);
        //check to see if this was the last round
        if (gameKeyDealerGame[_gameKey].currentRound == 10) {
            //the game is over when 10 rounds completed
            endGameAndDividePot(_gameKey);
        } else {
            //increment the round
            gameKeyDealerGame[_gameKey].currentRound += 1;
        }
    }

    //25% of the pot is divided between the players
    //who chose correctly
    function payOddEvenWinners(
        string memory _gameKey,
        bool _isOdd,
        uint256 _quarterPot
    ) internal {
        address[] memory oddEvenWinners;

        if (_isOdd) {
            oddEvenWinners = oddEvenPlayers[_gameKey][ODDEVEN_ODD];
        } else {
            oddEvenWinners = oddEvenPlayers[_gameKey][ODDEVEN_EVEN];
        }

        if (oddEvenWinners.length > 0) {
            uint256 oddEvenShare = _quarterPot / oddEvenWinners.length;

            //pay off each of the players in the array
            for (uint256 i = 0; i < oddEvenWinners.length; i++) {
                for (uint256 k = 0; k < 6; k++) {
                    if (
                        gameKeyDealerGame[_gameKey].players[k] ==
                        oddEvenWinners[i]
                    ) {
                        // add the share to the player's stack
                        gameKeyDealerGame[_gameKey].playerStacks[
                                k
                            ] += oddEvenShare;
                        // subtract the same amount from the pot
                        gameKeyDealerGame[_gameKey].potAmount -= oddEvenShare;

                        emit playerWon(
                            gameKeyDealerGame[_gameKey].players[k],
                            _gameKey,
                            _gameKey,
                            addressPlayerName[
                                gameKeyDealerGame[_gameKey].players[k]
                            ],
                            "Odds-Evens",
                            oddEvenShare,
                            gameKeyDealerGame[_gameKey].playerStacks[k],
                            gameKeyDealerGame[_gameKey].currentRound
                        );

                        break; //move on to the next player in the array
                    }
                }
            }
        }
        //set the players array to empty
        address[] memory emptyAddressArray;
        oddEvenPlayers[_gameKey][ODDEVEN_ODD] = emptyAddressArray;
        oddEvenPlayers[_gameKey][ODDEVEN_EVEN] = emptyAddressArray;
    }

    //25% of the pot is divided between the players
    //who chose correctly
    function payHighLowWinners(
        string memory _gameKey,
        bool _isLow,
        uint256 _quarterPot
    ) internal {
        address[] memory highLowWinners;
        if (_isLow) {
            highLowWinners = highLowPlayers[_gameKey][HIGHLOW_LOW];
        } else {
            highLowWinners = highLowPlayers[_gameKey][HIGHLOW_HIGH];
        }
        if (highLowWinners.length > 0) {
            uint256 highLowShare = _quarterPot / highLowWinners.length;

            //pay off each of the players in the array
            for (uint256 i = 0; i < highLowWinners.length; i++) {
                for (uint256 k = 0; k < 6; k++) {
                    if (
                        gameKeyDealerGame[_gameKey].players[k] ==
                        highLowWinners[i]
                    ) {
                        // add the share to the player's stack
                        gameKeyDealerGame[_gameKey].playerStacks[
                                k
                            ] += highLowShare;
                        // subtract the same amount from the pot
                        gameKeyDealerGame[_gameKey].potAmount -= highLowShare;

                        emit playerWon(
                            gameKeyDealerGame[_gameKey].players[k],
                            _gameKey,
                            _gameKey,
                            addressPlayerName[
                                gameKeyDealerGame[_gameKey].players[k]
                            ],
                            "High-Low",
                            highLowShare,
                            gameKeyDealerGame[_gameKey].playerStacks[k],
                            gameKeyDealerGame[_gameKey].currentRound
                        );

                        break; //move on to the next player in the array
                    }
                }
            }
        }
        //set the players array to empty
        address[] memory emptyAddressArray;
        highLowPlayers[_gameKey][HIGHLOW_LOW] = emptyAddressArray;
        highLowPlayers[_gameKey][HIGHLOW_HIGH] = emptyAddressArray;
    }

    //50% of the pot is divided between the players
    //who chose correctly
    function payExactMatchWinners(
        string memory _gameKey,
        uint256 _halfPot,
        uint256 _winningNumber
    ) internal {
        address[] memory exactNumberPlayers = numberPickPlayers[_gameKey][
            _winningNumber
        ];
        if (exactNumberPlayers.length > 0) {
            uint256 exactNumbersShare = _halfPot / exactNumberPlayers.length;
            //pay off each of the players in the array
            for (uint256 i = 0; i < exactNumberPlayers.length; i++) {
                for (uint256 k = 0; k < 6; k++) {
                    if (
                        gameKeyDealerGame[_gameKey].players[k] ==
                        exactNumberPlayers[i]
                    ) {
                        // add the share to the player's stack
                        gameKeyDealerGame[_gameKey].playerStacks[
                                k
                            ] += exactNumbersShare;
                        // subtract the same amount from the pot
                        gameKeyDealerGame[_gameKey]
                            .potAmount -= exactNumbersShare;

                        emit playerWon(
                            gameKeyDealerGame[_gameKey].players[k],
                            _gameKey,
                            _gameKey,
                            addressPlayerName[
                                gameKeyDealerGame[_gameKey].players[k]
                            ],
                            "Exact Number",
                            exactNumbersShare,
                            gameKeyDealerGame[_gameKey].playerStacks[k],
                            gameKeyDealerGame[_gameKey].currentRound
                        );

                        break; //move on to the next player in the array
                    }
                }
            }
        }
        //set all exact numbers player arrays to empty
        address[] memory emptyAddressArray;
        for (uint256 i = 1; i < 37; i++) {
            numberPickPlayers[_gameKey][i] = emptyAddressArray;
        }
    }

    //This will change the status of the game,
    //and if there is any money left in the pot
    //it will divide it equally and distribute
    //it back to the players
    function endGameAndDividePot(string memory _gameKey) internal {
        uint256 index = 0;
        //find the index of the game in currentGames array
        for (uint256 i = 0; i < currentGames.length; i++) {
            if (isSameString(currentGames[i], _gameKey)) {
                index = i;
                break;
            }
        }
        //remove the game from the currentGames array
        removeItemFromCurrentGamesArray(index);
        //set the status = ENDED
        uint256 endTime = block.timestamp;
        gameKeyDealerGame[_gameKey].gameStatus = GameStatus.ENDED;
        gameKeyDealerGame[_gameKey].endTime = endTime;

        if (gameKeyDealerGame[_gameKey].potAmount > 0) {
            //if there is money still in the pot then
            //split it evenly between the players
            uint256 playerCut = gameKeyDealerGame[_gameKey].potAmount /
                gameKeyDealerGame[_gameKey].playerCount;

            for (
                uint256 i = 0;
                i < gameKeyDealerGame[_gameKey].playerCount;
                i++
            ) {
                gameKeyDealerGame[_gameKey].playerStacks[i] += playerCut;
            }
        }
        gameKeyDealerGame[_gameKey].potAmount = 0;

        emit gameStatusChanged(
            msg.sender,
            _gameKey,
            _gameKey,
            endTime,
            GAME_ENDED_STRING
        );
    }

    //A dealer can have only one current game at a time
    function getDealerCurrentGame(address _dealer)
        internal
        returns (uint256 index, string memory gameKey)
    {
        string[] memory keys = dealerGameKeys[_dealer]; //get the gameKeys for the dealer
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

    //Remove ended games from array
    function removeItemFromCurrentGamesArray(uint256 _index) internal {
        //the easiest way to remove an item from the array in Solidity
        //is to copy the last item in the array over the
        //item to be deleted, then popping the last item off
        require(_index < currentGames.length);
        currentGames[_index] = currentGames[currentGames.length - 1];
        currentGames.pop();
    }

    //game keys must be unique
    function isGameKeyInUse(string memory _gameKey)
        internal
        view
        returns (bool)
    {
        //gameKey is in use if it has a non-null address in the gameKeyDealer mapping
        return
            gameKeyDealerGame[_gameKey].dealer !=
            0x0000000000000000000000000000000000000000;
    }

    //rules for allowing players to withdraw
    function checkAllowWithdrawal(string memory _gameKey)
        internal
        returns (bool allowWithdrawal, string memory message)
    {
        if (gameKeyDealerGame[_gameKey].gameStatus == GameStatus.ENDED) {
            return (true, "");
        }
        //There may be times when a dealer does not complete a game and
        //does not call endGame. If this happens there needs to be a way
        //for players of that game to retrieve their money.
        //Check to see if the game is over 1 hour old.
        //If so and a player wants to withdraw their money
        //end the game and allow the player to withdrawal.
        if (
            block.timestamp - gameKeyDealerGame[_gameKey].startTime >=
            GAME_TIMEOUT_IN_SECONDS
        ) {
            endGameAndDividePot(_gameKey);
            return (true, "");
        }
        return (false, "Cannot withdrawal at this time. Try again later.");
    }

    //rules for canceling a new game
    function checkCancelNewGame(string memory _gameKey, address dealer)
        internal
        returns (bool, string memory)
    {
        (, string memory currentGameKey) = getDealerCurrentGame(dealer);
        if (!isSameString(currentGameKey, _gameKey)) {
            return (false, "This is not the current game for the dealer.");
        }
        if (gameKeyDealerGame[_gameKey].playerCount > 0) {
            return (false, "Cannot cancel games once players have joined.");
        }
        return (true, "");
    }

    //rules for new games
    function checkNewGameRequirements(
        address _dealer,
        uint256 _dealerPayment,
        string memory _gameKey,
        uint256 _ante
    ) internal returns (bool success, string memory message) {
        //The owner can set the contract to not allow new games if needed
        if (!allowNewGames) {
            return (
                false,
                "New games not allowed at this time. Check back later."
            );
        }

        if (_dealerPayment < dealerFee) {
            return (false, "Not enough ETH!");
        }

        // The ante can be .001 eth, .01 eth or .1 eth
        if (
            _ante != ONE_ONETHOUSANDTH_ETH &&
            _ante != ONE_ONEHUNDREDTH_ETH &&
            _ante != ONE_TENTH_ETH
        ) {
            return (false, "Ante not a valid value.");
        }

        (, string memory currentGameKey) = getDealerCurrentGame(_dealer);
        if (!isSameString(currentGameKey, "")) {
            return (false, "You already have a game in progress.");
        }

        if (isGameKeyInUse(_gameKey)) {
            return (false, "GameKey already in use.");
        }
        if (randomNumberRequestLocked) {
            if (block.timestamp - randomNumberRequestLockTime > 300) {
                //this means the previous call to VRFConsumerBaseV2
                //to retrieve random numbers
                //has not returned and probably won't.
                //Reset and try again.
                randomNumberRequestLocked = false;
            } else {
                return (
                    false,
                    "Unable to initialize game at this time. Please wait a few minutes and try again."
                );
            }
        }

        return (true, "All conditions satisfied.");
    }

    //rules for joining a new game
    function checkJoinPlayerRequirements(
        string memory _gameKey,
        address _player,
        uint256 _fee
    ) internal returns (bool success, string memory message) {
        if (_fee < gameKeyDealerGame[_gameKey].ante * 10) {
            return (false, "Not enough ETH!");
        }
        string memory status = getGameStatus(_gameKey);
        if (isSameString(status, GAME_NOT_FOUND_STRING)) {
            return (false, status);
        }
        if (!isSameString(status, WAITING_FOR_PLAYERS_STRING)) {
            return (false, "Cannot join game at this time.");
        }
        if (playerIsInGame(_gameKey, _player)) {
            return (false, "Player already in game.");
        }
        return (true, "");
    }

    //rules for allowing a player to submit numbers
    function checkPlayerSubmitRequirements(
        string memory _gameKey,
        address _player
    ) internal view returns (bool success, string memory message) {
        if (!playerIsInGame(_gameKey, _player)) {
            return (false, "Player not in game.");
        }
        if (gameKeyDealerGame[_gameKey].gameStatus != GameStatus.IN_PROGRESS) {
            return (false, "Cannot submit numbers. Game is not in progress.");
        }
        if (hasPlayerSubmittedNumbers(_gameKey, _player)) {
            return (false, "Player already submitted numbers.");
        }
        if (gameKeyDealerGame[_gameKey].locked) {
            return (
                false,
                "Too many players submitting at one time. Please try again."
            );
        }
        return (true, "");
    }

    //rules for allowing dealer to set game to in progress
    function checkSetGameToInProgressRequirements(
        string memory _gameKey,
        address _dealer
    ) internal returns (bool success, string memory message) {
        (, string memory gameKey2) = getDealerCurrentGame(_dealer);
        if (isSameString(gameKey2, "")) {
            return (false, GAME_NOT_FOUND_STRING);
        }
        if (!isSameString(gameKey2, _gameKey)) {
            //Dealer can only have one current game at a time.
            return (false, "Game key is not current game for dealer.");
        }
        if (
            gameKeyDealerGame[_gameKey].gameStatus !=
            GameStatus.WAITING_FOR_PLAYERS
        ) {
            return (false, "Game already in progress or ended.");
        }
        if (gameKeyDealerGame[_gameKey].playerCount < 2) {
            return (
                false,
                "Two to six players required to play CryptoRoulette."
            );
        }

        return (true, "");
    }

    //find out if player in game
    function playerIsInGame(string memory _gameKey, address _player)
        internal
        view
        returns (bool)
    {
        for (uint256 i = 0; i < gameKeyDealerGame[_gameKey].playerCount; i++) {
            if (gameKeyDealerGame[_gameKey].players[i] == _player) {
                return true;
            }
        }
        return false;
    }

    //Comparing strings in Solidity doesn't work normally
    //So need to jump some hoops.
    function isSameString(string memory _string1, string memory _string2)
        internal
        view
        returns (bool)
    {
        return (keccak256(abi.encodePacked(_string1)) ==
            keccak256(abi.encodePacked(_string2)));
    }

    //players can only submit numbers once per round
    function hasPlayerSubmittedNumbers(string memory _gameKey, address _player)
        internal
        view
        returns (bool)
    {
        address[] memory playersHigh = highLowPlayers[_gameKey][HIGHLOW_HIGH];
        for (uint256 i = 1; i < playersHigh.length; i++) {
            if (playersHigh[i] == _player) {
                return true;
            }
        }
        address[] memory playersLow = highLowPlayers[_gameKey][HIGHLOW_LOW];
        for (uint256 i = 1; i < playersLow.length; i++) {
            if (playersLow[i] == _player) {
                return true;
            }
        }
        return false;
    }

    //Solidity does not like to concatenate strings the easy way
    function concatenateStrings(
        string memory a,
        string memory b,
        string memory c
    ) internal pure returns (string memory) {
        return string(bytes.concat(bytes(a), bytes(b), bytes(c)));
    }

    ////////////////////////////////////////////////////
    /////////////////////////////////////////////////////
    /////////////////////////////////////////////////////

    // ///Administrative functions
    function getCryptoRouletteBalance()
        external
        view
        onlyOwner
        returns (uint256)
    {
        return address(this).balance;
    }

    //Dealer's pay a fee when starting a new game
    //the cryptoRouletteBank variable holds the amount
    //of dealer fees added since the last withdrawal
    function getDealerFeeBalance() external view onlyOwner returns (uint256) {
        return cryptoRouletteBank;
    }

    //This is used to withdraw dealer fees from the contract.
    //This does not withdraw any eth owned by players.
    function withdrawDealerFees() external payable onlyOwner {
        uint256 amountToWithdraw = cryptoRouletteBank;
        cryptoRouletteBank = 0; //zero out the amount before transfer
        payable(msg.sender).transfer(amountToWithdraw);
    }

    function setDealerFee(uint256 _newDealerFee) external onlyOwner {
        dealerFee = _newDealerFee;
    }

    function setAllowNewGames(bool _allowNewGames) external onlyOwner {
        allowNewGames = _allowNewGames;
    }

    function storeRandomNumbers(
        string memory _gameKey,
        uint256[] memory _randomWords
    ) internal {
        if (_randomWords.length >= 10) {
            for (uint256 i = 0; i < 10; i++) {
                winningNumbers[_gameKey][i] = (_randomWords[i] % 36) + 1;
            }
            gameKeyDealerGame[_gameKey].gameStatus = GameStatus
                .WAITING_FOR_PLAYERS;
            emit gameStatusChanged(
                gameKeyDealerGame[_gameKey].dealer,
                _gameKey,
                _gameKey,
                block.timestamp,
                WAITING_FOR_PLAYERS_STRING
            );
            randomNumberRequestLocked = false;
        }
    }

    //////////////////////////////////////////////////////
    //for testing
    //Remove before going live

    function withdrawalAll() external payable onlyOwner {
        payable(msg.sender).transfer(address(this).balance);
    }

    ////////////////////////////////////////////////
}
