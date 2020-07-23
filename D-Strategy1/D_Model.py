# Import the model (if any):
from mlfinlab.online_portfolio_selection.pattern_matching import SCORN

# Import the logger:
import logging, time, websockets, json
import pandas as pd
from datetime import datetime
logger = logging.getLogger()

class DModelClass(object):

    ######################################## Receive data and model ########################################

    def _generateAllocationsDict(self, darwinsDataset):

        # NOTE: We get the dataframe with the actual close included.

        # Create object:
        self.window, self.rho = 3, 0.1
        self.PA_STRAT = SCORN(window=self.window, rho=self.rho)

        # Allocate:
        self.PA_STRAT.allocate(darwinsDataset, verbose=True)

        '''So, let's say that today 2020-06-26 previous to the auction (i.e. close of the market) I get all the data up to and including today, input that into the .allocate() method and the .weights attribute would be the weights that are chosen to execute PREVIOUS to the close of that same day (i.e. 2020-06-26). If you are buying at the next day open you are doing it wrong'''

        '''If no auction, just a bit before the close of the market so that you can compute weights and make the trading decisions.'''

        # Final weights:
        # Numpy array > FINAL_WEIGHTS = self.PA_STRAT.weights
        # DataFrame transposed:
        FINAL_WEIGHTS = self.PA_STRAT.all_weights.tail(1).T
        FINAL_WEIGHTS.columns = ['allocations']
        FINAL_WEIGHTS_DICT = FINAL_WEIGHTS.to_dict()

        '''Ex:
        
            2020-07-06 21:00:00
            HFD                  1.0
            SYO                  0.0
            KLG                  0.0'''

        logger.warning('FINAL PORTFOLIO WEIGHTS PREDICTION:')
        logger.warning(FINAL_WEIGHTS_DICT)
        # EX: {'HFD': -2797.31, 'SYO': 2513.46, 'KLG': -52.56}

        # Return it:
        return FINAL_WEIGHTS_DICT['allocations']

    ######################################## Receive data and model ########################################