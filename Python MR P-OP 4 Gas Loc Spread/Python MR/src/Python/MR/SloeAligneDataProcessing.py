import pandas as pd
import numpy as np
from numpy.lib.recfunctions import append_fields
import datetime

#Processing Aligne data. Numpy has been used to speed up the run

def readMeanRevertExcel(dateString):

    date = pd.to_datetime(dateString)

    if date.day < 10:
        day = '0'+str(date.day)
    else:
        day = str(date.day)

    if date.month < 10:
        month = '0' + str(date.month)
    else:
        month = str(date.month)

    year = str(date.year)

    nameString = 'MEAN_REVER_OPT_%s_%s_%s.xls' % (day,month,year)

    data = pd.read_excel('C:/Users/D110148/OneDrive - EP Commodities B.V/Modelos y Simulaciones/Mean Reversion Factor vs Aligne/%s' % (nameString)).dropna()
    
    return data.to_records(index=False)

def sortData(aligneInput):
    
    sort_indices = np.lexsort((aligneInput['C1_DELIVSTART'],aligneInput['C0_TNUM']))
    
    data = aligneInput[sort_indices]
    
    return data

def filteredByData(sortedData):

    # Retrieving the unique dates and the index of the first occurrence   
    firstOcc, firstOccInd = np.unique(sortedData['C1_DELIVSTART'], return_index= True)
    datetimes = firstOcc.astype('datetime64[D]')
    weekDay = np.is_busday(datetimes)
    secondOccInd = np.array([firstOccInd[i]+1 for i in range(len(firstOcc)) if weekDay[i] == True])

    # Determine peakness
    peakness = [np.nan for i in range(len(sortedData))]
    allOccInd = np.union1d(firstOccInd, secondOccInd)
    allOccInd.sort()
    for i in allOccInd:
        if i in firstOccInd:
            peakness[i] = 'offpeak'
        else:
            peakness[i] = 'peak'

    # Add the peakness list as a new column to sortedData
    sortedData = np.rec.array(append_fields(sortedData, 'peakness', np.array(peakness, dtype='<U7'), usemask=False))

    # Sort sorted data with allIndices mask
    sortedData = sortedData[allOccInd]

    #Take only CSS options
    data = sortedData[sortedData['C3_MC1_MC2'] == 'E_PHNL/TENNE2/SLOE/D']
    #data = sortedData[sortedData['C3_MC1_MC2'] == 'G_PHYS/TTF-MW/G_PHYS']   

    return data

def correctOldMRFactor(sAndFData, dateStringOld, dateString):

    #importing old MR Factors

    oldMRFactors = pd.read_excel('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/PEAK_MRF_BUCKET_STRUCTURE_' + dateStringOld + '.xlsx', sheet_name='Hoja1')
    oldMRFactorsArray = oldMRFactors.to_records()

    #Adding bucket dates to old MR factors recarray:

    date = pd.to_datetime(dateString).to_numpy()
    dates = [date + pd.Timedelta(days = oldMRFactorsArray.Bucket[i]) for i in range(len(oldMRFactorsArray.Bucket))]
    oldMRFactorsArray = np.rec.array(append_fields(oldMRFactorsArray, 'dates', np.array(dates), usemask=False, dtypes='datetime64[ns]'))

    #Getting indexes of those dates in the sortedData array:

    Ind = {date: np.where(sAndFData.C1_DELIVSTART == date)[0] for date in dates}
    Ind = [i[0] for i in Ind.values()]
    Ind.append(len(sAndFData))

    #Creating array to attach the MR Factors:

    MRlistToAppend = np.zeros([len(sAndFData),1])

    #Adding the MR to the array

    for i in range(len(oldMRFactors.MRFACTORS)):   #Review, it used to be len(Ind)
        MRlistToAppend[Ind[i]:Ind[i+1]] = oldMRFactors.MRFACTORS[i]

    True_MOD_VOL1 = sAndFData.C9_MOD_VOL1.reshape(-1,1) / MRlistToAppend

    True_MOD_VOL2 = sAndFData.C10_MOD_VOL2.reshape(-1,1) / MRlistToAppend

    sAndFData.C9_MOD_VOL1 = True_MOD_VOL1.reshape(1,-1)
    sAndFData.C10_MOD_VOL2 = True_MOD_VOL2.reshape(1,-1)

    return sAndFData


def correctedVolData1(sAndFData, dateString):

    # Load Excel data
    oldMRFactorsPeak = pd.read_excel('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/OFFPEAK_MRF_BUCKET_STRUCTURE_20240411.xlsx', sheet_name='Hoja1')
    oldMRFactorsOffPeak = pd.read_excel('C:/Users/D110148/OneDrive - EP Commodities B.V/Main - Risk Management/Risk Management OTS/Mean Reversion Aligne/PEAK_MRF_BUCKET_STRUCTURE_20240411.xlsx', sheet_name='Hoja1')
    oldMRFactorsPeakArray = oldMRFactorsPeak.to_records()
    oldMRFactorsOffPeakArray = oldMRFactorsOffPeak.to_records()

    # Adding bucket dates to old MR factors recarray
    date = np.datetime64(pd.to_datetime(dateString))  # Converting to numpy datetime64
    dates = [np.datetime64(date + pd.Timedelta(days=oldMRFactorsPeakArray.Bucket[i])) for i in range(len(oldMRFactorsPeakArray.Bucket))]
    oldMRFactorsPeakArray = np.rec.array(append_fields(oldMRFactorsPeakArray, 'dates', np.array(dates), usemask=False, dtypes='datetime64[ns]'))
    oldMRFactorsOffPeakArray = np.rec.array(append_fields(oldMRFactorsOffPeakArray, 'dates', np.array(dates), usemask=False, dtypes='datetime64[ns]'))

    # Splitting Peak and Offpeak recarrays
    peakData = sAndFData[sAndFData.peakness == 'peak']
    offpeakData = sAndFData[sAndFData.peakness == 'offpeak']

    # Ensure DELIVSTART is in numpy.datetime64 format
    sortedData = [peakData, offpeakData]
    MRlist = [oldMRFactorsPeakArray, oldMRFactorsOffPeakArray]
    outputList = []

    for j in range(len(sortedData)):
        # Ensure DELIVSTART is already in numpy.datetime64 format (as you confirmed)
        
        # Find the closest match or closest higher date for each date
        Ind = []
        for date in dates:
            exact_match = np.where(sortedData[j].DELIVSTART == date)[0]
            
            if exact_match.size > 0:
                Ind.append(exact_match[0])  # Exact match found
            else:
                # Use np.searchsorted to find the closest higher date
                pos = np.searchsorted(sortedData[j].DELIVSTART, date)
                if pos < len(sortedData[j]):  # Ensure the index is within bounds
                    Ind.append(pos)  # Closest higher index found
                else:
                    Ind.append(None)  # No valid higher date found (date is larger than any in array)
                    print(f"Warning: No valid higher date found for {date}. Check the data.")

        # Append the last index (boundary) to make slicing easier
        Ind.append(len(sortedData[j]))

        # Check for any None values in Ind and raise a warning
        if None in Ind:
            print(f"Warning: One or more dates in the dataset could not be matched to a valid higher date. Check data at index {Ind.index(None)}.")

        # Creating array to attach the MR Factors
        MRlistToAppend = np.zeros([len(sortedData[j]), 1])

        # Adding the MR to the array based on the calculated indices
        for i in range(len(Ind) - 1):
            if Ind[i] is not None:
                MRlistToAppend[Ind[i]:Ind[i + 1]] = MRlist[j].MRFACTORS[i]

        # Adjusting True_MOD_VOL1 and True_MOD_VOL2
        True_MOD_VOL1 = sortedData[j].C9_MOD_VOL1.reshape(-1, 1) / MRlistToAppend
        True_MOD_VOL2 = sortedData[j].C10_MOD_VOL2.reshape(-1, 1) / MRlistToAppend

        sortedData[j].C9_MOD_VOL1 = True_MOD_VOL1.reshape(1, -1)
        sortedData[j].C10_MOD_VOL2 = True_MOD_VOL2.reshape(1, -1)

        outputList.append(sortedData[j])

    return sAndFData, outputList[0], outputList[1]


def correctedVolData(sAndFData):

    peakData = sAndFData[sAndFData.peakness == 'peak']
    offpeakData = sAndFData[sAndFData.peakness == 'offpeak']
    
    return sAndFData, peakData, offpeakData
    
