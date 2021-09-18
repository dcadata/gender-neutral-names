import pandas as pd


class DataManager:
    _data_fp = 'data/data.csv'

    def __init__(self):
        self._years = tuple(range(1900, 2020 + 1))
        self.df = None
        self.summary = None
        self.ratio = None

    def load_data_from_disk(self):
        self.df = self._df.copy()

    def regenerate_data(self):
        self._read_all_files()
        self._calculate_percentages()
        self.df.to_csv(self._data_fp, index=False)

    def _read_all_files(self):
        dfs = [_read_one_file(f'data/yob{year}.txt').assign(year=year) for year in self._years]
        self.df = pd.concat(dfs)

    def _calculate_percentages(self):
        for year in self._years:
            self.df.loc[self.df.year == year, 'number_as_pct'] = (
                    self.df.loc[self.df.year == year, 'number'] / self.df.loc[self.df.year == year, 'number'].sum()
            )

    def add_fields(self):
        pct_of_births_table = self.df.groupby(by=['name', 'year'], as_index=False)['number_as_pct'].sum().rename(
            columns={'number_as_pct': 'pct_of_births'})
        self.df = self.df.merge(pct_of_births_table, on=['name', 'year'])
        self.df['ratio'] = self.df.number_as_pct / self.df.pct_of_births
        self.df['ratio_rank'] = self.df.ratio.apply(lambda x: x - 0.5)
        self.df['ratio_category'] = self.df.ratio_rank.apply(abs).apply(_categorize)

    def create_dataframes_to_plot(self):
        self.summary = self.df.groupby(by=['year', 'ratio_category'], as_index=False)['number_as_pct'].sum()
        self.ratio = self.df[['year', 'ratio_rank']]

    @property
    def _df(self):
        dtypes = {
            'name': str,
            'sex': str,
            'number': int,
            'year': int,
            'number_as_pct': float,
        }
        return pd.read_csv(self._data_fp, usecols=dtypes.keys(), dtype=dtypes)


def _read_one_file(filepath):
    df = pd.read_csv(filepath, names=['name', 'sex', 'number'], dtype={'name': str, 'sex': str, 'number': int})
    return df


def _categorize(x):
    if x <= 0.1:
        return '1: most neutral'
    if x <= 0.2:
        return '2: very neutral'
    if x <= 0.3:
        return '3: somewhat neutral'
    if x <= 0.4:
        return '4: mostly gendered'
    return '5: highly gendered'


def main():
    pass


if __name__ == '__main__':
    main()
