# First, we append the previous level to the sys.path var:
import sys, os
# We append the repository path to the sys.path so that we can import packages easily.
sys.path.append(os.path.expandvars('${HOME}/Desktop/quant-research-env/'))

# Import the different classes:
from darwinexapis.API.DarwinDataAnalyticsAPI.DWX_Data_Analytics_API import DWX_Darwin_Data_Analytics_API
from darwinexapis.API.InfoAPI.DWX_Info_API import DWX_Info_API
from darwinexapis.API.TradingAPI.DWX_Trading_API import DWX_Trading_API
from darwinexapis.API.InvestorAccountInfoAPI.DWX_AccInfo_API import DWX_AccInfo_API

# Import the logger:
import logging, time, websockets, json
import pandas as pd, numpy as np
from datetime import datetime
logger = logging.getLogger()

class DTestingMethods(object):

    def __init__(self):

        ### Let's create the auth credentials:
        self.AUTH_CREDS = {'access_token': 'c019d0e5-ee2e-3709-ae81-a48e26d1a583',
                           'consumer_key': 'Z4_p3FDLhI5x9pMlYWHvyiWW04Qa',
                           'consumer_secret': 'NR6hDOCbjJEfYzB2Hg1B9nfHhpAa',
                           'refresh_token': 'e58a759d-bbf8-3937-8dfe-7f576977994e'}

        # Create the objects:
        self._defineAPIObjects()

        # Call investorAccs at the beginning:
        self._listInvestorAccounts()

    ######################################## Auxiliary methods ########################################

    def _defineAPIObjects(self, isDemo=True):

        # Get the other APIs:
        self.INFO_API = DWX_Info_API(self.AUTH_CREDS, _version=2.0, _demo=isDemo)
        self.ACCOUNT_API = DWX_AccInfo_API(self.AUTH_CREDS, _version=2.0, _demo=isDemo)
        self.TRADING_API = DWX_Trading_API(self.AUTH_CREDS, _version=1.1, _demo=isDemo)

    def _checkInvalidCredentials(self, response, apiObject, methodCall):

        # Check for the text:
        if 'Invalid Credentials' in response:

            # Generate new credentials:
            logger.warning('[INVALID_CREDS] - Invalid credentials > ¡Generate TOKENS!')
            apiObject.AUTHENTICATION._get_access_refresh_tokens_wrapper()
        
            # Make the API call again:
            methodCall()

        else:
            # Creds are okey:
            logger.warning('[INVALID_CREDS] - Credentials are OKEY')

    def _assertRequestResponse(self, response):

        # Print response:
        logger.warning(response)

        # Print status_code and request boolean:
        #logger.warning(response.status_code)
        #logger.warning(response.ok)

    def _convertToDataFrame(self, response, filterOrNot):

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

    def _getClosesDataFrame(self, response):

        # Filter the dictionary and just get the close:
        self.newDict = {key : value['close'] for key, value in response.items()}

        # Convert to dataframe:
        DF_CLOSE = pd.DataFrame.from_dict(self.newDict)
        #DF_CLOSE.to_csv(os.path.expandvars('${HOME}/Desktop/quant-research-env/DARWINStrategyContentSeries/Data/') + 'ClosePricePortfolio.csv')
        DF_CLOSE.to_csv(os.path.expandvars('${HOME}/Desktop/') + 'ClosePricePortfolio.csv')
        print('DATAFRAME SAVED')

        # Drop NaNs:
        #logger.warning(f'Quantity of NaNs: {DF_CLOSE.isnull().sum().sum()}')
        DF_CLOSE.dropna(axis=0, inplace=True)
        DF_CLOSE.dropna(axis=1, inplace=True)
        #logger.warning(f'Quantity of NaNs: {DF_CLOSE.isnull().sum().sum()}')

        # Return it:
        return DF_CLOSE

    ######################################## Auxiliary methods ########################################

    ######################################## DARWIN APIs Requests ########################################

    def _listInvestorAccounts(self):

        # Get response:

        RETURNED_RESPONSE = self.ACCOUNT_API._Get_Accounts_()
        self._assertRequestResponse(RETURNED_RESPONSE)
        #self._checkInvalidCredentials(RETURNED_RESPONSE, self.ACCOUNT_API, self.ACCOUNT_API._Get_Accounts_)

        # Convert response:
        RETURNED_RESPONSE = self._convertToDataFrame(RETURNED_RESPONSE, [])

        # Get equity:
        self.investedFraction = RETURNED_RESPONSE.loc[0, 'invested'] / RETURNED_RESPONSE.loc[0, 'equity']
        logger.warning(self.investedFraction)

    def _currentPositions(self, accountID):

        # Get response:
        RETURNED_RESPONSE = self.ACCOUNT_API._Get_Current_Open_Positions_(_id=accountID)
        self._assertRequestResponse(RETURNED_RESPONSE)
        print('#################################################')

        # Convert response:
        if RETURNED_RESPONSE:
            RETURNED_RESPONSE = self._convertToDataFrame(RETURNED_RESPONSE, ['productName','invested','allocation','leverage','openPnl', 'currentQuote'])
            return RETURNED_RESPONSE
        else:
            # If positions are none, it will return an empty list.
            return

    def _getAllocationsAndTrades(self, finalAllocationsDF, accountID, totalAuMPercentage=0.95):

        # Get accounts and equity values:
        ACCOUNT_VALUES = self.ACCOUNT_API._Get_Accounts_()
        ACCOUNT_VALUES = self._convertToDataFrame(ACCOUNT_VALUES, [])

        # Get invested fraction with the equite and invested capital:
        equityValue = ACCOUNT_VALUES.loc[ACCOUNT_VALUES['id']==accountID, 'equity'][0] * totalAuMPercentage
        investedValue = ACCOUNT_VALUES.loc[ACCOUNT_VALUES['id']==accountID, 'invested'][0]
        investedFraction = round(investedValue / equityValue, 2)

        # Get the actual positions allocations:
        # The allocations are based on the actual positions equity, not on the total equity.
        ACTUAL_POSITIONS = self._currentPositions(accountID=accountID)
        ACTUAL_POSITIONS['allocation'] = ACTUAL_POSITIONS['allocation'] / 100

        # Change the names in the productName col:
        ACTUAL_POSITIONS['productName'] = ACTUAL_POSITIONS['productName'].apply(lambda x: x.split('.')[0])

        # Get the allocations based on all the equity:
        ACTUAL_POSITIONS['allocation_total'] = round(ACTUAL_POSITIONS['allocation'] * investedFraction, 2)

        # Get actual allocations apart:
        actualAllocationsSeries = ACTUAL_POSITIONS['allocation_total']

        # The DataFrame should have columns like final_allocations_total and productName
        # Concat the new DataFrame with the allocations for ALL the DARWINS (with and without positions):
        # It will create a new column called final_allocations_total.
        ACTUAL_POSITIONS_CONCAT = pd.concat([ACTUAL_POSITIONS, finalAllocationsDF], ignore_index=True).fillna(0)

        # Aggregate with last to get duplicates out and get the last ones:
        ACTUAL_POSITIONS_CONCAT_AGG = ACTUAL_POSITIONS_CONCAT.groupby('productName').agg('last').reset_index()

        # Do the final_allocations_total_capital and final_rebalances at the end:
        # Put the final_allocations_total_capital on a column:
        ACTUAL_POSITIONS['final_allocations_total_capital'] = round(ACTUAL_POSITIONS['final_allocations_total'] * equityValue, 2)
        logger.warning(ACTUAL_POSITIONS['final_allocations_total_capital'].sum())

        # Get the final rebalance values:
        ACTUAL_POSITIONS['final_rebalances'] = ACTUAL_POSITIONS['final_allocations_total_capital'] - ACTUAL_POSITIONS['invested']

        # Get view of the dataframe:
        TRADES = ACTUAL_POSITIONS[['productName', 'final_rebalances']].set_index('productName').to_dict()['final_rebalances']
        TRADES = {eachKey : round(eachValue, 2) for eachKey, eachValue in TRADES.items()}
        #TRADES_1 = ACTUAL_POSITIONS[['productName', 'final_allocations_total_capital']].set_index('productName').to_dict()['final_allocations_total_capital']
        #TRADES_1 = {eachKey : round(eachValue, 2) for eachKey, eachValue in TRADES_1.items()}

        ### TRIAL: APPEND ROWS 
        df = pd.read_csv('/home/eriz/Desktop/tries.csv', index_col=0)
        logger.warning(df)
        #ACTUAL_POSITIONS = ACTUAL_POSITIONS.concat(df)
        ACTUAL_POSITIONS.to_csv('/home/eriz/Desktop/tries2.csv')
        logger.warning(ACTUAL_POSITIONS)
        #logger.warning(TRADES)
        #logger.warning(TRADES_1)

    def _getAllocationsAndTradesNEW(self, finalAllocationsDict, accountID, totalAuMPercentage=0.95):

        # Get accounts and equity values:
        ACCOUNT_VALUES = self.ACCOUNT_API._Get_Accounts_()
        ACCOUNT_VALUES = self._convertToDataFrame(ACCOUNT_VALUES, [])

        # Get invested fraction with the equite and invested capital:
        equityValue = ACCOUNT_VALUES.loc[ACCOUNT_VALUES['id']==accountID, 'equity'][0] * totalAuMPercentage
        investedValue = ACCOUNT_VALUES.loc[ACCOUNT_VALUES['id']==accountID, 'invested'][0]
        investedFraction = round(investedValue / equityValue, 2)

        # Get the actual positions allocations:
        # The allocations are based on the actual positions equity, not on the total equity.
        ACTUAL_POSITIONS = self._currentPositions(accountID=accountID)
        ACTUAL_POSITIONS['allocation'] = ACTUAL_POSITIONS['allocation'] / 100

        # Change the names in the productName col:
        ACTUAL_POSITIONS['productName'] = ACTUAL_POSITIONS['productName'].apply(lambda x: x.split('.')[0])

        # Get the allocations based on all the equity:
        ACTUAL_POSITIONS['allocation_total'] = round(ACTUAL_POSITIONS['allocation'] * investedFraction, 2)
        logger.warning(ACTUAL_POSITIONS)

        # Get the dictionary of allocation_total + productName:
        ACTUAL_POS_DICT = ACTUAL_POSITIONS.set_index('productName').to_dict()['allocation_total']
        logger.warning(ACTUAL_POS_DICT)
        ACTUAL_POS_DICT = {'HFD': 0.56, 'SYO': 0.36, 'HLS': 0.08}
        logger.warning(ACTUAL_POS_DICT)

        # Pass to the trades calculation method:
        FINAL_ALLOCATIONS = self._finalTradesCalculation(ACTUAL_POS_DICT, finalAllocationsDict, equityValue)
        logger.warning(FINAL_ALLOCATIONS)

        # Return them:
        #return FINAL_ALLOCATIONS

    def _finalTradesCalculation(self, actualAlloDict, finalAlloDict, actualEquity):

        # Set the new dictionary:
        endAllocations = {}

        # We loop with the final allocations to the actual ones:
        for finalAsset, finalAllocation in finalAlloDict.items():

            for actualAsset, actualAllocation in actualAlloDict.items():

                # If we actually have a position in that asset, calculate:
                if actualAsset == finalAsset:
                    
                    # Get the change in capital we need to make:
                    capitalFinal = (finalAllocation * actualEquity) - (actualAllocation * actualEquity)
                    # Add it and add a boolean flag if we had actually the position (True) or not (False)
                    endAllocations[finalAsset] = [round(capitalFinal,2), True]

                # If we don't have a position, add it or not:
                elif actualAsset != finalAsset:

                    # If it is actually present, just pass.
                    if finalAsset in endAllocations:

                        pass

                    # If it is not, add it with the final allocation capital.
                    else:
                        # Get the capital we need to put there:
                        capitalFinal = finalAllocation * actualEquity
                        # Add it and add a boolean flag if we had actually the position (True) or not (False)
                        endAllocations[finalAsset] = [round(capitalFinal,2), False]

        # Return the final dictionary:
        return endAllocations

    def _closeAllPositions(self, accountID):

        # Close all positions:
        RETURNED_RESPONSE = self.TRADING_API._Close_All_Account_Trades_(_id=accountID)
        self._assertRequestResponse(RETURNED_RESPONSE)

        # Convert response:
        RETURNED_RESPONSE = self._convertToDataFrame(RETURNED_RESPONSE, [])

    def _closeDARWINPosition(self, accountID, darwinToClose):

        # Close specific darwin position:
        # darwinToClose can be the string of just the DARWIN name or with the suffix: KLG OR KLG.5.2
        RETURNED_RESPONSE = self.TRADING_API._Close_All_DARWIN_Trades_(_id=accountID, _darwin=darwinToClose)
        self._assertRequestResponse(RETURNED_RESPONSE)

        # Convert response:
        RETURNED_RESPONSE = self._convertToDataFrame(RETURNED_RESPONSE, [])

    ######################################## DARWIN APIs Requests ########################################

    ######################################## Analysis API ########################################

    def _createCandlePortfolio(self, symbols):

        # Get DARWINs:
        RETURNED_RESPONSE = self.INFO_API._Get_DARWIN_OHLC_Candles_(_symbols=symbols,
                                                                    _resolution='1d', # 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1mn
                                                                    _from_dt='2019-08-31 12:00:00', # UTC > All need to have data up to the this dt
                                                                    _to_dt=str(pd.Timestamp('now')),
                                                                    _timeframe='/ALL') # 1D, 1W, 1M, 3M, 6M, 1Y, 2Y, ALL
        self._assertRequestResponse(RETURNED_RESPONSE)

        # Create a dataframe with just the close of each DARWIN:
        RETURNED_RESPONSE = self._getClosesDataFrame(RETURNED_RESPONSE)
        logger.warning(RETURNED_RESPONSE)

        # Get actual quotes:
        ACTUAL_POSITIONS = self._currentPositions(accountID=2000062056)
        ACTUAL_POSITIONS_QUOTES = ACTUAL_POSITIONS['currentQuote'].values
        logger.warning(ACTUAL_POSITIONS_QUOTES)

        # Add last quote for every darwin:
        # Put the same timestamp as others.
        newData = pd.Series(ACTUAL_POSITIONS_QUOTES, 
                            index=RETURNED_RESPONSE.columns, 
                            name=datetime.now().replace(hour=21, minute=0, second=0, microsecond=0)) # name=datetime.now().strftime("%Y-%m-%d"))
        RETURNED_RESPONSE_2 = RETURNED_RESPONSE.append(newData, verify_integrity=True)
        logger.warning(RETURNED_RESPONSE_2)

    def _createFilteredPortfolio(self):

        # Get filtered DARWINs:
        while True:

            # If the hour is X, do something:
            #if datetime.now().hour == 9:

            RETURNED_RESPONSE = self.INFO_API._Get_Filtered_DARWINS_(_filters=[['d-score', 80, 100, 'actual'],
                                                                                #['drawdown', -10, 0, '6m'],
                                                                                ['return', 3, 100, '1m']],
                                                                        _order=['return','12m','DESC'],
                                                                        _page=0, # Sets the page we want to start from
                                                                        _perPage=50, # Sets the items per page we want to get
                                                                        _delay=1.0)
            self._assertRequestResponse(RETURNED_RESPONSE)
            FILTERED_DARWIN_SYMBOLS = RETURNED_RESPONSE['productName'].to_list()
            FILTERED_DARWIN_SYMBOLS = [eachSymbol.split('.')[0] for eachSymbol in FILTERED_DARWIN_SYMBOLS]
            logger.warning(FILTERED_DARWIN_SYMBOLS)

            # NOTE: Maintain the loop and recall the API to check if working.
            # Sleep for an hour more or less to not call any more in the day.
            time.sleep(60)

            #else:
            #    pass

    def _createLastQuotes(self, symbols):

        # Get DARWINs:
        RETURNED_RESPONSE = self.INFO_API._Get_DARWIN_OHLC_Candles_(_symbols=symbols,
                                                                    _resolution='1m', # 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1mn
                                                                    _from_dt=pd.to_datetime('today') - pd.to_timedelta(5, 'min'), 
                                                                    _to_dt=str(pd.Timestamp('now')),
                                                                    _timeframe='/ALL') # 1D, 1W, 1M, 3M, 6M, 1Y, 2Y, ALL
        self._assertRequestResponse(RETURNED_RESPONSE)

        # Create a dataframe with just the close of each DARWIN:
        RETURNED_RESPONSE = self._getClosesDataFrame(RETURNED_RESPONSE)
        logger.warning(RETURNED_RESPONSE)

        ACTUAL_POSITIONS_QUOTES = RETURNED_RESPONSE.iloc[-1, :].values
        logger.warning(ACTUAL_POSITIONS_QUOTES)

        # Add last quote for every darwin:
        # Put the same timestamp as others.
        newData = pd.Series(ACTUAL_POSITIONS_QUOTES, 
                            index=RETURNED_RESPONSE.columns, 
                            name=datetime.now().replace(hour=21, minute=0, second=0, microsecond=0)) # name=datetime.now().strftime("%Y-%m-%d"))
        RETURNED_RESPONSE_2 = RETURNED_RESPONSE.append(newData, verify_integrity=True)
        logger.warning(RETURNED_RESPONSE_2)

    ######################################## Analysis API ########################################

    ######################################## Other tests ########################################

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

    def _tradeDARWINPortfolio(self, tradesToExecuteDict, accountID):

        # First we need to SELL and then buy > Two loops:
        sellTrades = {eachKey: eachValue for eachKey, eachValue in tradesToExecuteDict.items() if eachValue < 0}
        logger.warning(sellTrades)
        buyTrades = {eachKey: eachValue for eachKey, eachValue in tradesToExecuteDict.items() if eachValue > 0}
        logger.warning(buyTrades)

        for eachProduct, eachQuantity in sellTrades.items():

            logger.warning('Selling loop initiated...')
            eachQuantityAbs = abs(eachQuantity)

            if 0 <= eachQuantityAbs <= 200:
                logger.warning('Amount lower than neccesary')
                # Don't do anything:
                # 200 USD is the minimum for new inv / 25 USD is the minimum to add
                pass

            else:
                # Sell:
                SELL_ORDER = self._generateSellOrder(eachProduct, eachQuantityAbs)
                RETURNED_RESPONSE = self.TRADING_API._Sell_At_Market(_id=accountID, _order=SELL_ORDER)
                self._assertRequestResponse(RETURNED_RESPONSE)

        logger.warning('¡Selling loop concluded!')

        for eachProduct, eachQuantity in buyTrades.items():

            logger.warning('Buying loop initiated...')

            if 0 <= eachQuantity <= 200:
                logger.warning('Amount lower than neccesary')
                # Don't do anything:
                # 200 USD is the minimum for new inv / 25 USD is the minimum to add
                pass

            else:
                # Buy:
                BUY_ORDER = self._generateBuyOrder(eachProduct, eachQuantity, {})
                RETURNED_RESPONSE = self.TRADING_API._Buy_At_Market_(_id=accountID, _order=BUY_ORDER)
                self._assertRequestResponse(RETURNED_RESPONSE)

        logger.warning('Buying loop concluded!')

if __name__ == "__main__":

    # Get it:
    DASSETUNIVERSE = DTestingMethods()
    #DASSETUNIVERSE._createFilteredPortfolio()
    DASSETUNIVERSE._currentPositions(accountID=2000069671)

    # This worked:
    #alloWeights = np.array([0.13, 0.65, 0.2105])
    #alloWeights = np.array([0.00, 0.65, 0.35])
    #alloWeights = {'HFD': 0.40, 'SYO': 0.10, 'HLS': 0.0, 'JKS': 0.30, 'OPQ': 0.20}
    #DASSETUNIVERSE._getAllocationsAndTrades(alloWeights, accountID=2000062056)
    #DASSETUNIVERSE._getAllocationsAndTradesNEW(alloWeights, accountID=2000062056)

    # This have worked:
    #DASSETUNIVERSE._closeDARWINPosition(accountID=2000062056, darwinToClose='KLG.5.2')
    #DASSETUNIVERSE._closeDARWINPosition(accountID=2000062056, darwinToClose='CIS')

    # This worked:
    # NOTE: Watch for starting dates, they might not be the same for all darwins!
    DASSETUNIVERSE._createCandlePortfolio(symbols=['PLF', 'SYO', 'ZVQ', 'OOS', 'CIS', 'ERQ'])
    #DASSETUNIVERSE._createCandlePortfolio(symbols=['HFD', 'SYO', 'KLG'])
    #DASSETUNIVERSE._createCandlePortfolio(symbols=['HFD.5.17', 'SYO.5.24', 'KLG.5.2'])
    #DASSETUNIVERSE._createLastQuotes(symbols=['PLF', 'SYO', 'ZVQ'])

    # This worked:
    #DASSETUNIVERSE._currentPositions(accountID=2000062056)
    #time.sleep(10)
    #DASSETUNIVERSE._closeAllPositions(accountID=2000062056)
    #time.sleep(4)
    #DASSETUNIVERSE._currentPositions(accountID=2000062056)

    # This worked:
    #tradesDict = {'SYO.5.24': -2513.46}
    #tradesDict = {'SYO.5.24': 2513.46, 'HFD.5.17': -2797.31, 'KLG.5.2': -52.56}
    #tradesDict = {'HFD.5.17': -2797.31}
    #tradesDict = {'KLG.5.2': -52.56}
    #DASSETUNIVERSE._tradeDARWINPortfolio(tradesDict, accountID=2000062056)
    