# Import the logger:
import logging, time, websockets, json
import pandas as pd
from datetime import datetime
logger = logging.getLogger()

class DAssetUniverseClass(object):

    ######################################## Auxiliary methods ########################################
    
    def _getClosesDataFrame(self, response):

        # Filter the dictionary and just get the close:
        self.newDict = {key : value['close'] for key, value in response.items()}

        # Convert to dataframe:
        DF_CLOSE = pd.DataFrame.from_dict(self.newDict)
        #DF_CLOSE.to_csv(os.path.expandvars('${HOME}/Desktop/quant-research-env/DARWINStrategyContentSeries/Data/') + 'ClosePricePortfolio.csv')

        # Drop NaNs:
        #logger.warning(f'Quantity of NaNs: {DF_CLOSE.isnull().sum().sum()}')
        DF_CLOSE.dropna(axis=0, inplace=True)
        DF_CLOSE.dropna(axis=1, inplace=True)
        #logger.warning(f'Quantity of NaNs: {DF_CLOSE.isnull().sum().sum()}')

        # Return it:
        return DF_CLOSE

    ######################################## Auxiliary methods ########################################

    ######################################## Analysis API ########################################

    def _createCandlePortfolio(self, symbols):

        # If we want filtered DARWINS, just pass the symbols to this method.
        # Products are ordered based on 'invested' capital.
        # Get positions to order them and send to the method.

        logger.warning('Will create candle portfolio of DARWINs...')

        # Get actual positions:
        ACTUAL_POSITIONS = self._currentPositions()

        # If we pass symbols, use them:
        # If they will be the same, no problem > Each time passing the same.
        if symbols:

            # Get response > We can put symbols with suffix or not.
            RETURNED_RESPONSE = self.INFO_API._Get_DARWIN_OHLC_Candles_(_symbols=symbols,
                                                                        _resolution='1d', # 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1mn
                                                                        _from_dt='2019-08-31 12:00:00', # UTC > All need to have data up to the this dt
                                                                        _to_dt=str(pd.Timestamp('now')),
                                                                        _timeframe='/ALL') # 1D, 1W, 1M, 3M, 6M, 1Y, 2Y, ALL
            self._assertRequestResponse(RETURNED_RESPONSE)

        # If the list is empty, get the actual ones:
        # If those are actually bought, use like this:
        else:

            # Get actual symbols:
            ACTUAL_SYMBOLS = ACTUAL_POSITIONS['productName'].to_list()
            # Get the suffix out:
            ACTUAL_SYMBOLS = [eachSymbol.split('.')[0] for eachSymbol in ACTUAL_SYMBOLS]

            # Get response > We can put symbols with suffix or not.
            RETURNED_RESPONSE = self.INFO_API._Get_DARWIN_OHLC_Candles_(_symbols=ACTUAL_SYMBOLS,
                                                                        _resolution='1d', # 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1mn
                                                                        _from_dt='2019-08-31 12:00:00', # UTC > All need to have data up to the this dt
                                                                        _to_dt=str(pd.Timestamp('now')),
                                                                        _timeframe='/ALL') # 1D, 1W, 1M, 3M, 6M, 1Y, 2Y, ALL
            self._assertRequestResponse(RETURNED_RESPONSE)

        # Get the actual positions quotes:
        try:
            # NOTE: It will through an error if no positions are available. 
            ACTUAL_POSITIONS_QUOTES = ACTUAL_POSITIONS['currentQuote'].values

            # Create a dataframe with just the close of each DARWIN:
            RETURNED_RESPONSE = self._getClosesDataFrame(RETURNED_RESPONSE)
            logger.warning('[CANDLE_PORTFOLIO] - Closes BEFORE todays data:')
            logger.warning(RETURNED_RESPONSE)

            # Add last quote for every darwin:
            # The actual quotes of this day won't be there (because we will execute PRIOR to the close), so just add it:
            newData = pd.Series(ACTUAL_POSITIONS_QUOTES, 
                                index=RETURNED_RESPONSE.columns, 
                                name=datetime.now().replace(hour=21, 
                                                            minute=0, 
                                                            second=0, 
                                                            microsecond=0))
            RETURNED_RESPONSE_2 = RETURNED_RESPONSE.append(newData, verify_integrity=True)
            logger.warning('[CANDLE_PORTFOLIO] - Closes AFTER todays data:')
            logger.warning(RETURNED_RESPONSE_2)

            # Return it:
            return RETURNED_RESPONSE_2

        except Exception as ex:

            logger.warning(f'CANDLE_PORTFOLIO - Exception: {ex}')

    def _createFilteredCandlePortfolio(self):

        # Get filtered DARWINs:
        while True:

            # If the hour is X, do something:
            if datetime.now().hour == 21 and datetime.now().minute == 56:

                RETURNED_RESPONSE = self.INFO_API._Get_Filtered_DARWINS_(_filters=[['d-score', 80, 100, 'actual'],
                                                                                  #['drawdown', -10, 0, '6m'],
                                                                                   ['return', 3, 100, '1m']],
                                                                        _order=['return','12m','DESC'],
                                                                        _page=0, # Sets the page we want to start from
                                                                        _perPage=50, # Sets the items per page we want to get
                                                                        _delay=1.0)
                self._assertRequestResponse(RETURNED_RESPONSE)

                # Get the symbols and delete the suffix:
                FILTERED_DARWIN_SYMBOLS = RETURNED_RESPONSE['productName'].to_list()
                FILTERED_DARWIN_SYMBOLS = [eachSymbol.split('.')[0] for eachSymbol in FILTERED_DARWIN_SYMBOLS]

                # Get those assets here:
                self._createCandlePortfolio(symbols=FILTERED_DARWIN_SYMBOLS)

            else:
                pass

    def _createFilteredPortfolio(self):

        # Get filtered DARWINs:
        while True:

            # If the hour is X, do something:
            if datetime.now().hour == 21 and datetime.now().minute == 56:

                RETURNED_RESPONSE = self.INFO_API._Get_Filtered_DARWINS_(_filters=[['d-score', 80, 100, 'actual'],
                                                                                  #['drawdown', -10, 0, '6m'],
                                                                                   ['return', 3, 100, '1m']],
                                                                        _order=['return','12m','DESC'],
                                                                        _page=0, # Sets the page we want to start from
                                                                        _perPage=50, # Sets the items per page we want to get
                                                                        _delay=1.0)
                self._assertRequestResponse(RETURNED_RESPONSE)

                # Return it:
                return RETURNED_RESPONSE

            else:
                pass

    ######################################## Analysis API ########################################