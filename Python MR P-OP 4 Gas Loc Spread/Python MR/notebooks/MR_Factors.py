
import pandas as pd
import datetime
import os
import sys

MR_dir = "C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/Python MR P-OP 4 Gas Loc Spread/Python MR/src/Python/MR/"
sys.path.insert(0,MR_dir)

import SloeAligneDataProcessing
import CSSMOModelDataProcessing
import MeanReversionFactorsCalc
import TransCapModule

#-------------------------------------------------------------------------------------

dateString = '20260217'

dateStringOld = '20260217'

MRFactor = '1'

#-------------------------------------------------------------------------------------

def RetrieveMODateString(dateString):

    dateMO = datetime.datetime.strptime(dateString, '%Y%m%d') + datetime.timedelta(1,0,0)

    if dateMO.day > 9:
        day = dateMO.day
    else:
        day = '0'+ str(dateMO.day)
        
    if dateMO.month > 9:
        month = dateMO.month
    else:
        month = '0'+ str(dateMO.month)

    dateStringMO = str(dateMO.year) + str(month) + str(day)

    return dateStringMO


def SloeAligneDataProcess(dateString,MRFactor):

    aligneInput = SloeAligneDataProcessing.readMeanRevertExcel(dateString)

    sortedData  = SloeAligneDataProcessing.sortData(aligneInput)

    sAndFData   = SloeAligneDataProcessing.filteredByData(sortedData)

    #sAndFData   = SloeAligneDataProcessing.correctOldMRFactor(sAndFData, dateStringOld, dateString)

    sAndFData, peakData, offpeakData = SloeAligneDataProcessing.correctedVolData(sAndFData)

    if all(sAndFData['C3_MC1_MC2'] =='E_PHNL/TENNE2/SLOE/D') == False:
        
        print('Warning: not all the deals left are CSS related')

    else:
        
        print('Data Processing succeded: All deals are CSS related')

    return sAndFData, peakData, offpeakData

    # sAndFData.dtype.fields
    # sAndFData.dtype.names


#------------------------------------------------------------------------------------------------------------------------------

#Processing Aligne Data:

AligneData, peakAligneData, offpeakAligneData = SloeAligneDataProcess(dateString, MRFactor)

pd.DataFrame(AligneData).to_csv('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/AligneData_'+dateString+'.csv')
pd.DataFrame(peakAligneData).to_csv('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/PeakAligneData_'+dateString+'.csv')
pd.DataFrame(offpeakAligneData).to_csv('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/OffpeakAligneData_'+dateString+'.csv')

#Processing MO Data:

dateStringMO = RetrieveMODateString(dateString)

#MOData, MODataP, MODataOP = CSSMOModelDataProcessing.DailyCssOptionValuation(dateStringMO)

transData = TransCapModule.readData(dateStringMO)

#Calculating Extrinsic:

MOIntrinsicImp        = transData['Import value -Intrinsic'][:-12]
MOExtrinsicImp        = transData['Import value -Extrinsic'][:-12]
MOTotalImp            = transData['Import value -Total'][:-12]

MOIntrinsicExp        = transData['Export value -Intrinsic'][:-12]
MOExtrinsicExp        = transData['Export value -Extrinsic'][:-12]
MOTotalExp            = transData['Export value -Total'][:-12]

months = list(set(AligneData['C1_DELIVSTART'].astype('datetime64[M]')))
months.sort()

meanReversionFactors        = MeanReversionFactorsCalc.getMeanReversionFactorArray(months, AligneData, MOIntrinsicExp)        #months, sAndFData, MOExtrinsic
meanReversionFactorsPeak    = MeanReversionFactorsCalc.getMeanReversionFactorArray(months, peakAligneData, MOExtrinsicExp)  #months, sAndFData, MOExtrinsic
meanReversionFactorsOffPeak = MeanReversionFactorsCalc.getMeanReversionFactorArray(months, offpeakAligneData, MOTotalExp)

pd.DataFrame({'MeanRevertFactors': meanReversionFactors}).to_csv('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/MeanReversionFactors ' + dateString + '.csv')
pd.DataFrame({'MeanRevertFactors': meanReversionFactorsPeak}).to_csv('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/MeanReversionFactorsPeak ' + dateString + '.csv')
pd.DataFrame({'MeanRevertFactors': meanReversionFactorsOffPeak}).to_csv('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/MeanReversionFactorsOffPeak ' + dateString + '.csv')
#Creating Aligne Data Frame with vols, underlying price, etc...:

AligneDfOutput        = MeanReversionFactorsCalc.addAligneData(months, AligneData)
AligneDfOutput.to_csv('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/AligneSummary' + dateString + '.csv')
AligneDfOutputPeak    = MeanReversionFactorsCalc.addAligneData(months, peakAligneData)
AligneDfOutputPeak.to_csv('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/AligneSummaryPeak' + dateString + '.csv')
AligneDfOutputOffPeak = MeanReversionFactorsCalc.addAligneData(months, offpeakAligneData)
AligneDfOutputOffPeak.to_csv('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/AligneSummaryOffPeak' + dateString + '.csv')

print(os.getcwd())

