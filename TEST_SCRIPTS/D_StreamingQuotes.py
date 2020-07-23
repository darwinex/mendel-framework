# First, we append the previous level to the sys.path var:
import sys, os
# We append the repository path to the sys.path so that we can import packages easily.
sys.path.append(os.path.expandvars('${HOME}/Desktop/quant-research-env/'))

# Import the base model:
from RegimeAnalysisContentSeries.Python_Classes.AssetClass import Asset
from RegimeAnalysisContentSeries.Python_Classes.ResearchStudyClass import ResearchStudy
from RegimeAnalysisContentSeries.Python_Classes.ModelClass import BaseModel
from RegimeAnalysisContentSeries.Python_Classes.FTP_DarwinAssets import FTP_CREDENTIALS

# Import the different classes:
from darwinexapis.API.DarwinDataAnalyticsAPI.DWX_Data_Analytics_API import DWX_Darwin_Data_Analytics_API
from darwinexapis.API.InfoAPI.DWX_Info_API import DWX_Info_API
from darwinexapis.API.InvestorAccountInfoAPI.DWX_AccInfo_API import DWX_AccInfo_API
from darwinexapis.API.WebSocketAPI.DWX_WebSocket_API import DWX_WebSocket_API

# Import the logger:
import logging, time, websockets, json
from datetime import datetime
logger = logging.getLogger()

class DGatewayClass(DWX_WebSocket_API):

    def __init__(self):

        ### Let's create the auth credentials:
        self.AUTH_CREDS = {'access_token': 'e42006fa-4007-3f11-b66a-ec699a8cb373',
                           'consumer_key': 'rEYfTTtu5xyyVgvXTZyTII7agpYa',
                           'consumer_secret': 'uNJLv0rPT_Gi5W2P_bY8ZVVfrGUa',
                           'refresh_token': '5bcbfd7a-d3a7-375c-9247-4759616c724f'}

        # Initialize the DWX_API class:
        super(DGatewayClass, self).__init__(_auth_creds=self.AUTH_CREDS, _version=0.0)

        # Create the objects:
        self._getObjects()

    ######################################## Analysis API ########################################

    def _getObjects(self, isDemo=True):

        # Get the FTP downloader:
        self.HISTORICAL_API = DWX_Darwin_Data_Analytics_API(dwx_ftp_user=FTP_CREDENTIALS['username'], 
                                                            dwx_ftp_pass=FTP_CREDENTIALS['password'],
                                                            dwx_ftp_hostname=FTP_CREDENTIALS['server'],
                                                            dwx_ftp_port=FTP_CREDENTIALS['port'])

        # Get the other APIs:
        self.INFO_API = DWX_Info_API(self.AUTH_CREDS, _version=2.0, _demo=isDemo)
        self.ACCOUNT_API = DWX_AccInfo_API(self.AUTH_CREDS, _version=2.0, _demo=isDemo)

    def _createPortfolio(self):

        self.portfolioSymbols = ['PLF.5.1', 'KLG.5.2']

    async def subscribe(self, _symbols=[]):
        
        #logger.warning(f'[SUBSCRIBE_UP] - AUTH_HEADERS: {self._auth_headers}')

        # Connect:
        ws = await websockets.connect(self._api_url, extra_headers=self._auth_headers)

        # Subscribe to symbols
        await ws.send(json.dumps({ 'op': 'subscribe', 'productNames' :_symbols}))
        logger.warning('[SUBSCRIBE] - CONNECTED to WS Server!')
           
        # If _active is True, process data received.
        while self._active:
               
            # Check for connection:
            if not ws.open:

                # Reconnect:
                try:
                    # Connect:
                    ws = await websockets.connect(self._api_url, extra_headers=self._auth_headers)

                    # Subscribe to symbols
                    await ws.send(json.dumps({ 'op': 'subscribe', 'productNames' :_symbols}))
                    logger.warning('[SUBSCRIBE] - ¡RECONNECTED to WS Server!')

                except Exception:
                    logger.warning('[SUBSCRIBE] - Unable to reconnect, trying again...')

            # While active, do work:
            try:
                # If the time is greater that the time + the expires in > issue refresh:
                if time.time() > self.AUTHENTICATION.expires_in:

                    logger.warning('[SUBSCRIBE] - The expiration time has REACHED > ¡Generate TOKENS!')
                    # Generate new token:
                    self.AUTHENTICATION._get_access_refresh_tokens_wrapper()

                    # Re-run the loop:
                    logger.warning('[SUBSCRIBE] - Need to re-run the loop with new TOKENS...')
                    return

                else:
                    logger.warning('[SUBSCRIBE] - The expiration time has NOT reached yet > Continue...')

                # Keep returning:
                self._ret = await ws.recv()
               
                ###################### Insert your Quote handling logic here ######################
                # {"op":"hb","timestamp":1587838905842} > Heartbeats.
                # Reference: https://api.darwinex.com/store/site/pages/doc-viewer.jag?docName=Product%20Quotes%20WebSocket%20subscription%20walkthroughname=QuoteWebSocket& version=1.0.0&provider=admin&
                #logger.warning(self._ret)
                #logger.warning(type(self._ret))
                self._handleQuoteStream(self._ret)
                #logger.warning(f'RETURNED MESSAGE: {self._ret}')
                ###################### Insert your Quote handling logic here ######################
            
            except Exception as ex:
                logger.warning(f'[SUBSCRIBE] - Ex: {ex}')

    def _streamPortfolioData(self):

        self.run(_symbols=self.portfolioSymbols)

    def _handleQuoteStream(self, quote):

        try: 
            # Convert to JSON:
            quote = json.loads(quote)

            # Get op type:
            opType = quote['op']

            # Filter:
            if opType == 'pq':

                assetName = quote['productName']
                assetQuote = quote['quote']
                assetTimeStamp = datetime.utcfromtimestamp(quote['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')
                logger.warning(f'PRODUCT QUOTE - TS: {assetTimeStamp} >>> Asset: {assetName} // Quote: {assetQuote}')

            elif opType == 'subscribed':
                
                # Get the quotes:
                quotes = quote['products']

                # Loop the products list:
                for eachAsset in quotes:
                    assetName = eachAsset['productName']
                    assetQuote = eachAsset['quote']
                    logger.warning(f'SUBS - Asset: {assetName} // Quote: {assetQuote}')

        except Exception as ex:
            logger.warning(f'Ex: {ex}')

    ######################################## APIs ########################################

if __name__ == "__main__":

    # Get it:
    DGATEWAY = DGatewayClass()
    DGATEWAY._createPortfolio()
    DGATEWAY._streamPortfolioData()
