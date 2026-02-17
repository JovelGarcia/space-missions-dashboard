import pandas as pd

path = 'space_missions.csv'


def load_file(filepath):
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filepath}' not found")
    except Exception as e:
        raise Exception(f"Error loading file: {e}")


def getMissionCountByCompany(companyName: str) -> int:
    """
    Function 1
    :param companyName: name of company
    :return: total # number of missions
    """
    if not companyName or not isinstance(companyName, str):
        raise ValueError("Company name must be a non-empty string")

    df = load_file(path)

    if companyName not in df['Company'].values:
        raise ValueError(f"Company '{companyName}' not found in database")

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
    if not companyName or not isinstance(companyName, str):
        raise ValueError("Company name must be a non-empty string")

    df = load_file(path)

    if companyName not in df['Company'].values:
        raise ValueError(f"Company '{companyName}' not found in database")

    company_df = df[(df['Company'] == companyName)]
    total_count = len(company_df)

    success_count = len(company_df[company_df['MissionStatus'] == 'Success'])

    if total_count == 0 or success_count == 0:
        return 0.0

    return round((success_count / total_count) * 100, 2)


def getMissionsByDateRange(startDate: str, endDate: str) -> list:
    """
    Function 3
    :param startDate: start date in "YYYY-MM-DD" format
    :param endDate: end date in "YYYY-MM-DD" format
    :return: list of missions within start and end date
    """
    if not startDate or not endDate:
        raise ValueError("Start date and end date must be provided")

    df = load_file(path)

    try:
        df['Date'] = pd.to_datetime(df['Date'])
        start = pd.to_datetime(startDate)
        end = pd.to_datetime(endDate)
    except Exception as e:
        raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {e}")

    if start > end:
        raise ValueError("Start date cannot be after end date")

    min_date = df['Date'].min()
    max_date = df['Date'].max()

    if start > max_date or end < min_date:
        raise ValueError(f"Date range is outside database bounds ({min_date.date()} to {max_date.date()})")

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
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer")

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
    if not isinstance(year, int):
        raise ValueError("Year must be an integer")

    df = load_file(path)

    try:
        df['Date'] = pd.to_datetime(df['Date'])

        min_year = df['Date'].dt.year.min()
        max_year = df['Date'].dt.year.max()

        if year < min_year or year > max_year:
            raise ValueError(f"Year {year} is outside database bounds ({min_year} to {max_year})")

        missions_count = df[df['Date'].dt.year == year]
        return len(missions_count)
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Error processing year: {e}")


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
    if not isinstance(startYear, int) or not isinstance(endYear, int):
        raise ValueError("Years must be integers")

    if startYear > endYear:
        raise ValueError("Start year cannot be after end year")

    df = load_file(path)

    try:
        df['Date'] = pd.to_datetime(df['Date'])
        df['Year'] = df['Date'].dt.year

        min_year = df['Year'].min()
        max_year = df['Year'].max()

        if startYear > max_year or endYear < min_year:
            raise ValueError(f"Year range is outside database bounds ({min_year} to {max_year})")

        if startYear < min_year or endYear > max_year:
            raise ValueError(
                f"Year range ({startYear} to {endYear}) outside database bounds ({min_year} to {max_year})")

        filtered_df = df[(df['Year'] >= startYear) & (df['Year'] <= endYear)]
        total_years = endYear - startYear + 1

        total_missions = len(filtered_df)
        average = total_missions / total_years

        return round(average, 2)
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Error calculating average: {e}")

def getTopCompaniesByMissionCountInRange(n: int, startDate: str, endDate: str) -> list:
    """
    getMissionsByDateRange + getTopCompaniesByMissionCount

    :param n: # of companies to return
    :param startDate: start date in "YYYY-MM-DD" format
    :param endDate: end date in "YYYY-MM-DD" format
    :return:
        - list of tuples [(companyName, missionCount), ...]
            missionCount in descending order
            companyName in ascending order for ties
    """
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer")

    if not startDate or not endDate:
        raise ValueError("Start date and end date must be provided")

    df = load_file(path)

    try:
        df['Date'] = pd.to_datetime(df['Date'])
        start = pd.to_datetime(startDate)
        end = pd.to_datetime(endDate)
    except Exception as e:
        raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {e}")

    if start > end:
        raise ValueError("Start date cannot be after end date")

    min_date = df['Date'].min()
    max_date = df['Date'].max()

    if start > max_date or end < min_date:
        raise ValueError(f"Date range is outside database bounds ({min_date.date()} to {max_date.date()})")

    filtered_df = df[(df['Date'] >= start) & (df['Date'] <= end)]

    company_counts = filtered_df['Company'].value_counts().reset_index()
    company_counts.columns = ['Company', 'Count']

    company_counts = company_counts.sort_values(
        by=['Count', 'Company'],
        ascending=[False, True]
    )

    top_n = company_counts.head(n)

    return list(zip(top_n['Company'], top_n['Count']))


def getSummaryStatistics() -> dict:
    """
    Returns overall summary statistics for the entire dataset (unfiltered).

    :return: dictionary with keys:
        - 'total_missions': int
        - 'overall_success_rate': float (rounded to 2 decimal places)
        - 'total_companies': int
        - 'avg_missions_per_year': float (rounded to 2 decimal places)
        - 'most_used_rocket': str
        - 'year_range': tuple (min_year, max_year)
    """
    df = load_file(path)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year

    total_missions = len(df)
    success_count = (df['MissionStatus'] == 'Success').sum()
    overall_success_rate = round((success_count / total_missions * 100), 2) if total_missions > 0 else 0.0
    total_companies = df['Company'].nunique()

    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())
    total_years = max_year - min_year + 1
    avg_missions_per_year = round(total_missions / total_years, 2)

    most_used_rocket = getMostUsedRocket()

    return {
        'total_missions': total_missions,
        'overall_success_rate': overall_success_rate,
        'total_companies': total_companies,
        'avg_missions_per_year': avg_missions_per_year,
        'most_used_rocket': most_used_rocket,
        'year_range': (min_year, max_year),
    }


# try:
#     print(getMissionStatusCount())
# except ValueError as e:
#     print(f"Validation Error: {e}")
# except FileNotFoundError as e:
#     print(f"File Error: {e}")
# except Exception as e:
#     print(f"Error: {e}")