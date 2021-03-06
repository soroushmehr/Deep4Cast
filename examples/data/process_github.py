import numpy as np
import pandas as pd
import argparse
import os

from pandas.tseries.holiday import USFederalHolidayCalendar as calendar


def prepare_data(data_path):
    """Returns dataframe with features."""

    # Get data
    df = pd.read_csv(data_path)

    # Remove NaNs
    df = df.dropna()

    # Convert date to datetime
    df['date'] = pd.to_datetime(df.date)

    # Create and age variable
    df['age'] = df.index.astype('int')

    # Create a day of week field
    df['day'] = df.date.dt.dayofweek

    # Create a month of year field
    df['month'] = df.date.dt.month

    # Create a boolean for US federal holidays
    holidays = calendar().holidays(start=df.date.min(), end=df.date.max())
    df['holiday'] = df['date'].isin(holidays).apply(int)

    # Rearrange columns
    df = df[
        [
            'date',
            'count',
            'age',
            'month',
            'day',
            'holiday'
        ]
    ]

    # Create monthly dummies
    tmp = pd.get_dummies(df.month)
    tmp.columns = ['month' + str(value) for value in tmp.columns]
    df = pd.concat([df, tmp], axis=1)

    # Create daily dummies
    tmp = pd.get_dummies(df.day)
    tmp.columns = ['day' + str(value) for value in tmp.columns]
    df = pd.concat([df, tmp], axis=1)

    # Reset index
    df = df.reset_index(drop=True)

    # Log transform count data
    df['count'] = np.log1p(df['count'])

    # Drop unnecessary columns
    df = df.drop(['month', 'day', 'age'], axis=1)
    df = df.dropna()

    return df


def run():
    parser = argparse.ArgumentParser(description='Prepare data')
    parser.add_argument('--data_path',
                        default='raw/github_dau_2011-2018.csv')
    parser.add_argument('--output_path',
                        default='processed/github_dau_2011-2018.pkl')
    args = parser.parse_args()

    # Get the data
    df = prepare_data(args.data_path)

    # Store data
    path = os.path.dirname(args.output_path)
    if not os.path.exists(path):
        os.makedirs(path)
    df.to_pickle(args.output_path, protocol=4)


if __name__ == '__main__':
    run()
