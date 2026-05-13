#CODE FOR DAILY BASELOAD CSS OPTION VALUATION FUNCTION #THIS IS THE ONE THAT WORKS!!
#LOOK INTO THE POSSIBILITY TO PASS IT TO NUMPY IN THE FUTURE TO SPEED UP THE RUN

def emptyFunction():

    return 1


def readData(date):

    import pandas as pd
    import glob
    import os
    import numpy as np
    import datetime as datetime
    import time

    def listPatternFiles(searchDir, pattern):
        files = glob.glob(os.path.join(searchDir, pattern), recursive = True)
        return files

    #Track time:

    start = time.time()
    
    #Read the hourly power data:

    today = pd.to_datetime(date)
    tYear = today.year
    tMonth = today.month
    tDay = today.day
    
    strMonth = ''
    strDay = ''

    if len(str(tMonth)) < 2:
        strMonth = '0'+str(tMonth)
    else:
        strMonth = str(tMonth)

    if len(str(tDay)) < 2:
        strDay = '0'+str(tDay)
    else:
        strDay = str(tDay)

    pattern = 'GasLocationSpread_'+str(tYear)+strMonth+strDay+'.csv'    
    #searchDir = 'I:/BU Portfolio Analytics/Market Analysis/Power/Models & Tools/Merit Order/PDP/Summary Outputs/'
    searchDir = 'C:/Users/D110148/OneDrive - EP Commodities B.V/Modelos y Simulaciones/Mean Reversion Factor vs Aligne/'
    data = pd.read_csv(listPatternFiles(searchDir, pattern)[0], sep = ",")

    #Process the format and transform it to daily data:

  

    data.to_csv('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/CSSMoMonthlyExtrinsic'+str(tYear)+strMonth+strDay+'.csv')


    end = time.time() - start

    print('MO Data processed succesfully, %s seconds employed' % end)
    
    return data

    
