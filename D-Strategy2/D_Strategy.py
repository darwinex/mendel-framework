# Import the different classes:
from darwinexapis.API.DarwinDataAnalyticsAPI.DWX_Data_Analytics_API import DWX_Darwin_Data_Analytics_API
from darwinexapis.API.InfoAPI.DWX_Info_API import DWX_Info_API
from darwinexapis.API.TradingAPI.DWX_Trading_API import DWX_Trading_API
from darwinexapis.API.InvestorAccountInfoAPI.DWX_AccInfo_API import DWX_AccInfo_API

# Import other classes:
from D_AssetUniverse import DAssetUniverseClass
from D_Model import DModelClass
from telegramBot import NotificationsTelegramBot

# Import the logger:
import logging, time, websockets, json
import pandas as pd
from datetime import datetime
logger = logging.getLogger()

class DStrategyClass(DAssetUniverseClass, DModelClass):

    def __init__(self, accountID):

        # Initialize the objects:
        self._defineAPIObjects()

        # Create the accountID:
        self.accountID = accountID

        # Create bot object:
        self.BOT = NotificationsTelegramBot("992949032:AAFg_BkkVL215WeO9rLHcaknKSsG4CjFdCk", -284176084)

    ######################################## Auxiliary methods ########################################

    def _loadJSONCredentials(self):

        # Load the file and return it:
        with open('APICredentials.json') as json_file:
            self.AUTH_CREDS = json.load(json_file)

    def _saveJSONCredentials(self, credentials):

        # Save then to the file to be accesed by other classes:
        with open('APICredentials.json') as json_file:
            json.dump(credentials, json_file)

    def _defineAPIObjects(self, isDemo=True):

        # Let's create the auth credentials:
        self._loadJSONCredentials()

        # Get the other APIs:
        self.INFO_API = DWX_Info_API(self.AUTH_CREDS, _version=2.0, _demo=isDemo)
        self.ACCOUNT_API = DWX_AccInfo_API(self.AUTH_CREDS, _version=2.0, _demo=isDemo)
        self.TRADING_API = DWX_Trading_API(self.AUTH_CREDS, _version=1.1, _demo=isDemo)

    def _assertRequestResponse(self, response):

        # Print response:
        logger.warning(response)

    def _checkInvalidCredentials(self, response, apiObject, methodCall):

        # Check for the text:
        if 'Invalid Credentials' in response:

            # Generate new credentials:
            logger.warning('[INVALID_CREDS] - Invalid credentials > ¡Generate TOKENS!')
            apiObject.AUTHENTICATION._get_access_refresh_tokens_wrapper()

            # Save the credentials:
            self._saveJSONCredentials(apiObject.AUTHENTICATION._auth_creds)

            # Create the objects AND load the NEW credentials:
            self._defineAPIObjects()

            # Make the API call again:
            methodCall()

        else:
            # Creds are okey:
            logger.warning('[INVALID_CREDS] - Credentials are OKEY')

    def _convertToDataFrame(self, response, filterOrNot):

        # Depending on the type we will be able to filter one way or another
        try:

            if isinstance(response, list):

                if filterOrNot:
                    response = pd.DataFrame(response)[filterOrNot]
                    logger.warning(response)

                else:
                    response = pd.DataFrame(response)
                    logger.warning(response)

                return response

            elif isinstance(response, dict):

                if filterOrNot:
                    response = pd.DataFrame.from_dict([response])[filterOrNot]
                    logger.warning(response)

                else:
                    response = pd.DataFrame.from_dict([response])
                    logger.warning(response)

                return response
        
        except Exception as ex:
            logger.warning(f'EXCEPTION > Could not convert to DataFrame: {ex}')
            return None

    def _generateBuyOrder(self, productName, quantity, thresholdParameters):

        return json.dumps({
          "amount": quantity,
          "productName": productName,
          "thresholdParameters": thresholdParameters
        })

    def _generateSellOrder(self, productName, quantity):

        return json.dumps({"amount": quantity,
                           "productName": productName
        })

    ######################################## Auxiliary methods ########################################

    ######################################## DARWIN APIs Requests ########################################

    def _listInvestorAccountsAndTest(self):

        # Get response:
        RETURNED_RESPONSE = self.ACCOUNT_API._Get_Accounts_()
        self._assertRequestResponse(RETURNED_RESPONSE)

        # Check for invalid credentials:
        self._checkInvalidCredentials(RETURNED_RESPONSE, self.ACCOUNT_API, self.ACCOUNT_API._Get_Accounts_)

        # Convert response:
        RETURNED_RESPONSE = self._convertToDataFrame(RETURNED_RESPONSE, [])

    def _currentPositions(self):

        # Get response:
        RETURNED_RESPONSE = self.ACCOUNT_API._Get_Current_Open_Positions_(_id=self.accountID)
        self._assertRequestResponse(RETURNED_RESPONSE)

        # Convert response:
        if RETURNED_RESPONSE:
            RETURNED_RESPONSE = self._convertToDataFrame(RETURNED_RESPONSE, ['productName','invested','allocation','leverage','openPnl', 'currentQuote'])
            return RETURNED_RESPONSE
        else:
            # If positions are none, it will return an empty list.
            return

    def _closeAllPositions(self):

        # Close all positions:
        RETURNED_RESPONSE = self.TRADING_API._Close_All_Account_Trades_(_id=self.accountID)
        self._assertRequestResponse(RETURNED_RESPONSE)

        # Convert response:
        RETURNED_RESPONSE = self._convertToDataFrame(RETURNED_RESPONSE, [])

    def _closeDARWINPosition(self, darwinToClose):

        # Close specific darwin position:
        # darwinToClose can be the string of just the DARWIN name or with the suffix: KLG OR KLG.5.2
        RETURNED_RESPONSE = self.TRADING_API._Close_All_DARWIN_Trades_(_id=self.accountID, _darwin=darwinToClose)
        self._assertRequestResponse(RETURNED_RESPONSE)

        # Convert response:
        RETURNED_RESPONSE = self._convertToDataFrame(RETURNED_RESPONSE, [])

    ######################################## DARWIN APIs Requests ########################################

    ######################################## Analysis API ########################################

    def _executeStrategy(self):

        # Check for valid credentials with a call to the API:
        self._listInvestorAccountsAndTest()

        # Generate DARWINs dataset:
        DARWINS_DATASET = self._createCandlePortfolio(symbols=['PLF', 'SYO', 'ZVQ', 'OOS', 'CIS', 'ERQ'])

        # Get the allocations for today:
        ALLOCATIONS = self._generateAllocationsDict(DARWINS_DATASET)

        # Get final to-do trades:
        TRADES = self._getAllocationsAndTrades(ALLOCATIONS)

        # Do the trades:
        self._tradeDARWINPortfolio(TRADES)

    def _getAllocationsAndTrades(self, finalAllocationsDict, totalAuMPercentage=0.95):

        '''The equity value already incorporates the openPnL (unrealized) > Real-time Total Equity.
        Leaving a small amount in the account will help if residuals are left over in transactions.'''

        # Get the actual positions allocations:
        # The allocations are based on the actual positions equity (invested sum), not on the total equity.
        # Call this previous to _Get_Accounts_ so that we have less latency in real-time equity value.
        ACTUAL_POSITIONS = self._currentPositions()
        ACTUAL_POSITIONS['allocation'] = ACTUAL_POSITIONS['allocation'] / 100

        # Change the names in the productName col:
        ACTUAL_POSITIONS['productName'] = ACTUAL_POSITIONS['productName'].apply(lambda x: x.split('.')[0])

        # Get accounts and equity values:
        ACCOUNT_VALUES = self.ACCOUNT_API._Get_Accounts_()
        ACCOUNT_VALUES = self._convertToDataFrame(ACCOUNT_VALUES, [])

        # Get invested fraction with the equity and invested capital:
        equityValue = ACCOUNT_VALUES.loc[ACCOUNT_VALUES['id']==self.accountID, 'equity'][0] * totalAuMPercentage
        logger.warning(f'EQUITY VALUE: {equityValue}')
        investedValue = ACCOUNT_VALUES.loc[ACCOUNT_VALUES['id']==self.accountID, 'invested'][0]
        logger.warning(f'INVESTED VALUE: {investedValue}')
        investedFraction = round(investedValue / equityValue, 2)
        logger.warning(f'INVESTED FRACTION: {investedFraction}')

        # Get the allocations based on all the equity:
        ACTUAL_POSITIONS['allocation_total'] = round(ACTUAL_POSITIONS['allocation'] * investedFraction, 2)

        # Get the dictionary of allocation_total + productName:
        ACTUAL_POS_DICT = ACTUAL_POSITIONS.set_index('productName').to_dict()['allocation_total']
        logger.warning(f'ACTUAL POSITIONS FOR DT: <{datetime.now()}>')
        logger.warning(ACTUAL_POS_DICT)

        # Pass to the trades calculation method:
        FINAL_CAPITAL_ALLOCATIONS = self._finalTradesCalculation(ACTUAL_POS_DICT, finalAllocationsDict, equityValue)
        logger.warning(f'FINAL CAPITAL ALLOCATIONS FOR DT: <{datetime.now()}>')
        logger.warning(FINAL_CAPITAL_ALLOCATIONS)

        # Return them:
        return FINAL_CAPITAL_ALLOCATIONS

    def _finalTradesCalculation(self, actualAlloDict, finalAlloDict, actualEquity):

        # Set the new dictionary:
        EXECUTION_ALLOCATIONS = {}

        # We loop with the final allocations to the actual ones:
        for finalAsset, finalAllocation in finalAlloDict.items():

            for actualAsset, actualAllocation in actualAlloDict.items():

                # If we actually have a position in that asset, calculate:
                if actualAsset == finalAsset:
                    
                    # Get the change in capital we need to make:
                    capitalFinal = (finalAllocation * actualEquity) - (actualAllocation * actualEquity)
                    # Add it and add a boolean flag if we had actually the position (True) or not (False)
                    EXECUTION_ALLOCATIONS[finalAsset] = [round(capitalFinal,2), True]

                # If we don't have a position, add it or not:
                elif actualAsset != finalAsset:

                    # If it is actually present (i.e we have added it previously in the loop), just pass.
                    if finalAsset in EXECUTION_ALLOCATIONS:

                        pass

                    # If it is not, add it with the final allocation capital.
                    else:
                        # Get the capital we need to put there:
                        capitalFinal = finalAllocation * actualEquity
                        # Add it and add a boolean flag if we had actually the position (True) or not (False)
                        EXECUTION_ALLOCATIONS[finalAsset] = [round(capitalFinal,2), False]

        # Return the final dictionary:
        return EXECUTION_ALLOCATIONS

    def _tradeDARWINPortfolio(self, tradesToExecuteDict):

        logger.warning(f'TRADE_PORTFOLIO - Trading datetime is: <{datetime.now()}>')

        # Ex: {'HFD': [-1486.9, True], 'SYO': [-2416.21, True], 'HLS': [-743.45, True], 'JKS': [2787.93, False], 'OPQ': [1858.62, False]}
        sellTrades = {eachKey: eachValue for eachKey, eachValue in tradesToExecuteDict.items() if eachValue[0] < 0}
        buyTrades = {eachKey: eachValue for eachKey, eachValue in tradesToExecuteDict.items() if eachValue[0] > 0}

        # First we need to SELL and then buy > Two loops:
        # SELL LOOP:
        for eachProduct, (eachQuantity, presenceBoolean) in sellTrades.items():

            logger.warning('TRADE_PORTFOLIO - Selling loop initiated...')
            eachQuantityAbs = abs(eachQuantity)

            # If we have actually a position on that asset.
            if presenceBoolean:
                try:
                    # 25 USD is the minimum to sell
                    assert eachQuantityAbs >= 25

                    # Sell:
                    SELL_ORDER = self._generateSellOrder(eachProduct, eachQuantityAbs)
                    logger.warning(f'SELL ORDER GENERATED FOR {eachProduct} WITH QUANTITY {eachQuantityAbs}:')
                    logger.warning(SELL_ORDER)
                    RETURNED_RESPONSE = self.TRADING_API._Sell_At_Market(_id=self.accountID, _order=SELL_ORDER)
                    self._assertRequestResponse(RETURNED_RESPONSE)

                except AssertionError:
                    logger.warning('TRADE_PORTFOLIO - Amount lower than neccesary')
            
            # If we don't have actually a position on that asset.
            else:
                # Doesn't apply as it is a sell > We will sell if we have a position:
                logger.warning('TRADE_PORTFOLIO - Does not apply as it is a sell action')

        logger.warning('TRADE_PORTFOLIO - ¡Selling loop concluded!')

        # BUY LOOP:
        for eachProduct, (eachQuantity, presenceBoolean) in buyTrades.items():

            logger.warning('TRADE_PORTFOLIO - Buying loop initiated...')

            # If we have actually a position on that asset.
            if presenceBoolean:
                try:
                    # 25 USD is the minimum to add
                    assert eachQuantityAbs >= 25

                    # Buy:
                    BUY_ORDER = self._generateBuyOrder(eachProduct, eachQuantity, {})
                    logger.warning(f'BUY ORDER GENERATED FOR {eachProduct} WITH QUANTITY {eachQuantityAbs}:')
                    logger.warning(BUY_ORDER)
                    RETURNED_RESPONSE = self.TRADING_API._Buy_At_Market_(_id=self.accountID, _order=BUY_ORDER)
                    self._assertRequestResponse(RETURNED_RESPONSE)

                except AssertionError:
                    logger.warning('TRADE_PORTFOLIO - Amount lower than neccesary')
            
            # If we don't have actually a position on that asset.
            else:
                try:
                    # 200 USD is the minimum to get a position
                    assert eachQuantityAbs >= 200

                    # Buy:
                    BUY_ORDER = self._generateBuyOrder(eachProduct, eachQuantity, {})
                    logger.warning('BUY ORDER GENERATED:')
                    logger.warning(BUY_ORDER)
                    RETURNED_RESPONSE = self.TRADING_API._Buy_At_Market_(_id=self.accountID, _order=BUY_ORDER)
                    self._assertRequestResponse(RETURNED_RESPONSE)

                except AssertionError:
                    logger.warning('TRADE_PORTFOLIO - Amount lower than neccesary')

        logger.warning('TRADE_PORTFOLIO - Buying loop concluded!')

    ######################################## Analysis API ########################################

if __name__ == "__main__":

    DSTRATEGY = DStrategyClass(accountID=2000069671)

    ### Get it into the method:
    DSTRATEGY._executeStrategy()