from mage_ai.data_cleaner.transformer_actions.base import BaseAction
from mage_ai.data_cleaner.transformer_actions.constants import ActionType, Axis
from mage_ai.data_cleaner.transformer_actions.utils import build_transformer_action
import pandas as pd
from pandas import DataFrame
from datetime import datetime
import numpy as np


if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def execute_transformer_action(df: DataFrame, *args, **kwargs) -> DataFrame:
    
    # Convert the 'Date' column to the desired date format
    df['Date'] = df['Date'].apply(lambda x: datetime.strptime(x, '%d-%b-%y').strftime('%Y-%m-%d'))
    

    Result = df['Result']
    HomeTeam_goals = Result.str[0]
    AwayTeam_goals = Result.str[-1]

    df.insert(3,'HomeTeam_goals', HomeTeam_goals)
    df.insert(4,'AwayTeam_goals', AwayTeam_goals)
    df.drop(columns=['Result'], inplace=True)
    
    return df

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
