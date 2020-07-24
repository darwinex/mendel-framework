# Import the different classes:
from darwinexapis.API.InfoAPI.DWX_Info_API import DWX_Info_API
from telegramBot import NotificationsTelegramBot

# Import the logger:
import logging, json
logger = logging.getLogger()

class DRefresherClass(object):

    '''Service to be executed at X timeframe and refresh the tokens.
    
    Ex (execute every 30 min): */30 * * * * start-refresher.sh'''

    def __init__(self):

        # Create bot object:
        self.BOT = NotificationsTelegramBot("1159315823:AAFexwCPKJvMeulDnS-he3NCeAjWqcTgejY", 779773830)

        # Initialize the objects:
        self._defineAPIObjects()

        # Execute:
        self._executeRefresh()

    def _defineAPIObjects(self, isDemo=True):

        # Let's create the auth credentials:
        self._loadJSONCredentials()

        # Get the other APIs:
        self.INFO_API = DWX_Info_API(self.AUTH_CREDS, _version=2.0, _demo=isDemo)

    def _executeRefresh(self):

        # Generate new credentials:
        logger.warning('[REFRESH_CREDS] - Time to refresh > ¡Generate TOKENS!')
        self.INFO_API.AUTHENTICATION._get_access_refresh_tokens_wrapper()

        # If failed, new access token will attribute will be None:
        if self.INFO_API.AUTHENTICATION._auth_creds.access_token:

            # Save the credentials:
            self._saveJSONCredentials(self.INFO_API.AUTHENTICATION._auth_creds)
        
        else:
            logger.warning('[REFRESH_CREDS] - Credentials NOT RETRIEVED')
            self.BOT.bot_send_msg('[REFRESH_CREDS] - Credentials NOT RETRIEVED')

    def _loadJSONCredentials(self):

        # Load the file and return it:
        with open('APICredentials.json') as json_file:
            self.AUTH_CREDS = json.load(json_file)

        # Log:
        logger.warning('[CREDS_LOAD] - ¡Credentials loaded!')

    def _saveJSONCredentials(self, credentials):

        # Save then to the file to be accesed by other classes:
        with open('APICredentials.json', 'w') as json_file:
            json.dump(credentials, json_file)

        # Log:
        logger.warning('[CREDS_SAVE] - ¡Credentials saved!')

        # Concluded:
        self.BOT.bot_send_msg('[CREDS_SAVE] - ¡Credentials saved and concluded!')

if __name__ == "__main__":

    # Create the object:
    DREFRESHER = DRefresherClass()