import pandas as pd

path = 'space_missions.csv'

class DataLoadError(Exception):
    """Custom exception for data loading errors"""
    pass

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def load_file(filepath):
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        return None
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

def getMissionCountByCompany(companyName: str) -> int:
    """
    Function 1
    :param companyName: name of company
    :return: total # number of missions
    """
    df = load_file(path)

    company_df = df[(df['Company'] == companyName)]
    mission_count = len(company_df)

    return mission_count

def getSuccessRate(companyName: str) -> float:
    """
    Function 2
    success rate is (total # of missions counted as successful) / (total # of missions)

    :param companyName: name of company
    :return: success rate rounded to 2 decimal places, or 0.0 if company has no missions
    """
    df = load_file(path)

    # Not utilized, since this would need to load the dataframe again
    # total_count = getMissionCountByCompany(companyName)

    company_df = df[(df['Company'] == companyName)]
    total_count = len(company_df)

    success_count = len(company_df[company_df['MissionStatus'] == 'Success'])

    if total_count == 0 or success_count == 0:
        return 0.0

    return round((success_count / total_count)*100, 2)

def getMissionsByDateRange(startDate: str, endDate: str) -> list:
    """
    Function 3
    :param startDate: start date in "YYYY-MM-DD" format
    :param endDate: end date in "YYYY-MM-DD" format
    :return: list of missions within start and end date
    """

    df = load_file(path)

    df['Date'] = pd.to_datetime(df['Date'])

    start = pd.to_datetime(startDate)
    end = pd.to_datetime(endDate)

    dated_df = df[(df['Date'] >= start) & (df['Date'] <= end)]

    return dated_df['Mission'].to_list()

def getTopCompaniesByMissionCount(n: int) -> list:
    """
    Function 4
    :param n: # of companies to return
    :return:
        - list of tuples [(companyName, missionCount), ...]
            missionCount is descending order
            companyName in ascending order
    """

    df = load_file(path)

    company_counts = df['Company'].value_counts().reset_index()
    company_counts.columns = ['Company', 'Count']

    company_counts = company_counts.sort_values(
        by=['Count', 'Company'],
        ascending=[False, True]
    )

    top_n = company_counts.head(n)

    return list(zip(top_n['Company'], top_n['Count']))

def getMissionStatusCount() -> dict:
    """
    Function 5
    :return:
        - dictionary: ( key: 'MissionStatus', value: 'count')
    """

    df = load_file(path)

    status_counts = df['MissionStatus'].value_counts()

    return status_counts.to_dict()

def getMissionsByYear(year: int) -> int:
    """
    Function 6
    :param year: Year
    :return: Total # of missions in that year
    """

    df = load_file(path)

    df['Date'] = pd.to_datetime(df['Date'])

    missions_count = df[df['Date'].dt.year == year]

    return len(missions_count)

def getMostUsedRocket() -> str:
    """
    Function 7
    :return: Rocket name
        - if rockets have same count, return first one alphabetically
    """
    df = load_file(path)

    rocket_df = df['Rocket'].value_counts().reset_index()
    rocket_df.columns = ['Rocket', 'Count']

    rocket_df = rocket_df.sort_values(
        by=['Count', 'Rocket'],
        ascending=[False, True]
    )

    return rocket_df.iloc[0]['Rocket']

def getAverageMissionsPerYear(startYear: int, endYear: int) -> float:
    """
    Function 8
    :param startYear: starting year
    :param endYear: ending year
    :return: average missions per year
        - rounded to 2 decimal places
    """

    df = load_file(path)

    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year

    filtered_df = df[(df['Year'] >= startYear) & (df['Year'] <= endYear)]
    total_years = endYear - startYear + 1

    total_missions = len(filtered_df)
    average = total_missions/total_years

    return round(average, 2)

print(getAverageMissionsPerYear(2010, 2020))

