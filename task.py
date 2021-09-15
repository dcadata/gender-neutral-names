import pandas as pd


class DataManager:
    def __init__(self):
        self._years = tuple(range(1900, 2020 + 1, 10))  #

    def _read_all_files(self):
        dfs = [_read_one_file(f'data/yob{year}.txt').assign(year=year) for year in self._years]
        self.df = pd.concat(dfs)

    def _calculate_percentages(self):
        for year in self._years:
            total_births = self.df.loc[self.df.year == year, 'number'].sum()
            self.df.loc[self.df.year == year, 'pct'] = self.df.loc[self.df.year == year, 'number'] / total_births
            for sex in ('F', 'M'):
                condition = (self.df.year == year) & (self.df.sex == sex)
                total_births = self.df.loc[condition, 'number'].sum()
                self.df.loc[condition, 'pct_sex'] = self.df.loc[condition, 'number'] / total_births

    def _calculate_gender_neutrality(self):
        pass


def _read_one_file(filepath):
    df = pd.read_csv(filepath, names=['name', 'sex', 'number'], dtype={'name': str, 'sex': str, 'number': int})
    return df
