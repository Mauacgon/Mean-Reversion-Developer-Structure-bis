#CODE FOR DAILY BASELOAD CSS OPTION VALUATION FUNCTION #THIS IS THE ONE THAT WORKS!!
#LOOK INTO THE POSSIBILITY TO PASS IT TO NUMPY IN THE FUTURE TO SPEED UP THE RUN

def emptyFunction():

    return 1


def DailyCssOptionValuation(date):

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

    pattern = 'Daily_'+str(tYear)+strMonth+strDay+'*HourlyReleveld.csv'    
    #searchDir = 'I:/BU Portfolio Analytics/Market Analysis/Power/Models & Tools/Merit Order/PDP/Summary Outputs/'
    searchDir = 'C:/Users/D110148/OneDrive - EP Commodities B.V/Modelos y Simulaciones/Mean Reversion Factor vs Aligne/'
    HourlyData = pd.read_csv(listPatternFiles(searchDir, pattern)[0], sep = ";")

    #Process the format and transform it to daily data:

    HourlyData['VALUEDATETIME'] = pd.to_datetime(HourlyData['VALUEDATETIME'])
    HourlyData = HourlyData[HourlyData['VALUEDATETIME'] >= pd.Timestamp(today)]
    HourlyData['day'] = [str(i.year) + '-' + str(i.month) + '-' + str(i.day) for i in HourlyData['VALUEDATETIME']]

    #Creating peak and offpeak DataFrames:

    peakMask = [(i.hour > 7 and i.hour < 21) if i.weekday() < 5 else False for i in HourlyData.VALUEDATETIME]

    HourlyPeak = HourlyData[peakMask]
    HourlyOffPeak = HourlyData[[not i for i in peakMask]]

    dfList = [HourlyData, HourlyPeak, HourlyOffPeak]
    outputList = []

    for df in dfList:


        df = df.groupby('day').agg(np.mean)
        df.index = [pd.to_datetime(i) for i in df.index]
        df.sort_index(inplace=True)

        outputList.append(df)

    HourlyData, HourlyPeak, HourlyOffPeak = outputList

     # Read gas and carbon daily data:

    pattern = 'Daily_'+str(tYear)+strMonth+strDay+'*BASE CASE_Daily.csv'
    gasAndCarbon = pd.read_csv(listPatternFiles(searchDir, pattern)[0], sep = ";")

     # Process the format:

    gasAndCarbon['VALUEDATETIME'] = pd.to_datetime(gasAndCarbon['VALUEDATETIME'])
    gasAndCarbon = gasAndCarbon[gasAndCarbon['VALUEDATETIME'] >= pd.Timestamp(today)]
    gasAndCarbon.index = gasAndCarbon['VALUEDATETIME']
    gasAndCarbon =  gasAndCarbon.iloc[:,1:]

     # Creating separated dataframes for Carbon and gas from the previous dataframe and setting their index:

    carbonList  = ['CARBON_Sim_'+str(i) for i in range(1,501)]
    gasList     = ['GAS_Sim_'+str(i) for i in range(1,501)]
    carbonData  = gasAndCarbon[carbonList]
    carbonDataP = carbonData[[i in HourlyPeak.index for i in  carbonData.index]]
    gasData     = gasAndCarbon[gasList]
    gasDataP    = gasData[[i in HourlyPeak.index for i in  carbonData.index]]
    for i in outputList:
        i.drop(columns=['VALUEDATETIME'], inplace=True)
    #carbonData.index, gasData.index = (gasAndCarbon['VALUEDATETIME'] for i in range(1,3))
    #carbonDataP.index, gasDataP.index = (gasAndCarbon['VALUEDATETIME'] for i in range(1,3))
    

    #Creating CSS database (the efficiency is understated, but this happened to be conservative):

    dfpList = outputList  #HourlyData, HourlyPeak, HourlyOffPeak                                 
    dfgList = [gasData, gasDataP, gasData]
    dfcList = [carbonData, carbonDataP, carbonData]
    outputList = []

    for i in range(3):

        CssDaily = pd.DataFrame(dfpList[i].values - 1.91900818*dfgList[i].values - 0.353084*dfcList[i].values)
        CssDaily.columns = ['CSS_NL_Sim_'+str(i) for i in range(1,501)]
        CssDaily.index = dfpList[i].index
        CssDaily['Year&Month'] = [str(i.year)+ '-' + str(i.month) for i in CssDaily.index]

        #adding weights in case it is OFFPEAK:

        CssDaily['weight'] = [0.5 if i.weekday() < 5 else 1 for i in dfpList[i].index]

        #Creating CSS fwd curve:

        if dfpList[i] is not HourlyOffPeak:

            CssMonthlyFWD = CssDaily.groupby('Year&Month').agg(np.mean).T.mean().T

        else:

            CssMonthlyFWD = CssDaily.groupby('Year&Month').agg(lambda x: np.average(x, weights=CssDaily.loc[x.index, 'weight'], axis=0)).T.mean().T

        CssMonthlyFWD.index = pd.to_datetime(CssMonthlyFWD.index)
        CssMonthlyFWD.sort_index(inplace = True)

        #Creating CSS fwd option value:

        CssDaily = CssDaily.iloc[:,:-2]
        CssDailyOption = pd.DataFrame(CssDaily.where(CssDaily > 0,0))
        CssDailyOption['Year&Month'] = [str(i.year)+'-'+str(i.month) for i in CssDailyOption.index]
        CssOptMonthly = CssDailyOption.groupby('Year&Month').agg(np.mean)
        CssOptMonthly.index = pd.to_datetime(CssOptMonthly.index)
        CssOptMonthly.sort_index(inplace = True)
        CssOptMonthly = CssOptMonthly.T.mean().T

        #Creating Monthly intrinsic:

        CssDailyAvg = CssDaily.T.mean()
        CssDailyIntr = pd.DataFrame(CssDailyAvg.where(CssDailyAvg>0,0))
        CssDailyIntr['Year&Month'] = [str(i.year) + '-' +str(i.month) for i in CssDailyIntr.index]
        CssMonthlyIntr=CssDailyIntr.groupby('Year&Month').agg(np.mean)
        CssMonthlyIntr.index = pd.to_datetime(CssMonthlyIntr.index)
        CssMonthlyIntr.sort_index(inplace=True)
        CssMonthlyIntr = pd.Series(CssMonthlyIntr[0])

    #Creating Final Data Frame:

        data = pd.DataFrame({'Forward_CSS': CssMonthlyFWD,
                    'Forward_Option_Css':CssOptMonthly,
                            'Forward_Intr':CssMonthlyIntr,
                    'Forward_Extrinsic':CssOptMonthly - CssMonthlyIntr})
        
        outputList.append(data)

    data, dataP, dataOP = outputList

    #Saving CSV:

    data.to_csv('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/CSSMoMonthlyExtrinsic'+str(tYear)+strMonth+strDay+'.csv')
    dataP.to_csv('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/CSSMoMonthlyExtrinsicP'+str(tYear)+strMonth+strDay+'.csv')
    dataOP.to_csv('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/CSSMoMonthlyExtrinsicOP'+str(tYear)+strMonth+strDay+'.csv')

    end = time.time() - start

    print('MO Data processed succesfully, %s seconds employed' % end)
    
    return data, dataP, dataOP

    
