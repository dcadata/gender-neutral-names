import pandas as pd
import seaborn as sns


class DataManager:
    def __init__(self):
        self._data_fp = 'data/data.csv'
        self._years = tuple(range(1900, 2020 + 1))
        self.df = None
        self._pct_of_births_table = None
        self.summary = None
        self.opp = None

    def load_data_from_disk(self):
        self.df = self._df.copy()

    def create_dataframes_to_plot(self):
        self._pct_of_births_table = self.df.groupby(by=['name', 'year'], as_index=False)['pct'].sum().rename(columns={
            'pct': 'pct_of_births'})
        self.df = self.df.merge(self._pct_of_births_table, on=['name', 'year'])
        self.df['ratio'] = self.df.pct / self.df.pct_of_births
        self.df['ratio_rank'] = self.df.ratio.apply(lambda x: x - 0.5)
        self.df['category'] = self.df.ratio_rank.apply(abs).apply(_categorize)
        self.summary = self.df.groupby(by=['year', 'category'], as_index=False)['pct'].sum()

    def calculate_neutral_names_by_yob(self):
        df = self.df.loc[~self.df.category.str.startswith('5'), [
            'year', 'name', 'category', 'sex', 'ratio', 'number']].copy()
        df.ratio = df.ratio.apply(lambda x: round(x, 3))
        df = df[df.sex == 'F'].merge(df[df.sex == 'M'], on=['year', 'name', 'category'], suffixes=('_f', '_m')).drop(
            columns=['sex_f', 'sex_m'])
        df['number'] = df.number_f + df.number_m
        year_dfs = dict(
            (year, df[df.year == year].sort_values('number', ascending=False).drop(columns=['number']))
            for year in self._years
        )
        for year, year_df in year_dfs.items():
            year_df.to_csv(f'neutral_names_by_yob/{year}.csv', index=False)
        pd.concat(year_dfs.values()).to_csv('neutral_names_by_yob/!all.csv', index=False)

    def calculate_opposite_gendered_name_trends(self):
        df = self.df.loc[self.df.category.str.startswith('5'), ['name', 'sex', 'year', 'ratio']].copy()
        df = df[df.sex == 'F'].merge(df[df.sex == 'M'], on=['name', 'year'], suffixes=('_f', '_m')).drop(columns=[
            'sex_f', 'sex_m'])
        df['ratio_cat'] = (df.ratio_f - df.ratio_m).apply(lambda x: 'F' if x > 0 else 'M')
        df = df.merge(self.df[['name', 'year', 'sex', 'pct']], on=['name', 'year'])
        df = df[df.ratio_cat != df.sex].groupby(by=['year', 'sex', 'ratio_cat'], as_index=False).pct.sum()
        self.opp = df.copy()

    def _regenerate_data(self):
        self._read_all_files()
        self._calculate_percentages()
        self.df.to_csv(self._data_fp, index=False)

    def _read_all_files(self):
        self.df = pd.concat(_read_one_file(f'data/yob{year}.txt').assign(year=year) for year in self._years)

    def _calculate_percentages(self):
        for year in self._years:
            self.df.loc[self.df.year == year, 'pct'] = (
                    self.df.loc[self.df.year == year, 'number'] / self.df.loc[self.df.year == year, 'number'].sum()
            )

    @property
    def _df(self):
        dtypes = {
            'name': str,
            'sex': str,
            'number': int,
            'year': int,
            'pct': float,
        }
        return pd.read_csv(self._data_fp, usecols=dtypes.keys(), dtype=dtypes)


class Plotter(DataManager):
    def plot_all_categories(self):
        plot = sns.pointplot(x='year', y='pct', hue='category', data=self.summary, palette='husl')
        fig = plot.get_figure()
        fig.autofmt_xdate()
        fig.set_size_inches(12, 8)
        fig.suptitle('Percentage of births accounted for by names in each category, 1900 to latest')
        fig.savefig('img/categories.png')

    def plot_neutral_categories(self):
        plot = sns.pointplot(x='year', y='pct', hue='category', data=self.summary[
            ~self.summary.category.str.startswith('5')], palette='husl')
        fig = plot.get_figure()
        fig.autofmt_xdate()
        fig.set_size_inches(12, 8)
        fig.suptitle('Percentage of births accounted for by gender-neutral names in each category, 1900 to latest')
        fig.savefig('img/categories_neutral.png')

    def plot_opposite_gendered_name_trends(self):
        plot = sns.pointplot(x='year', y='pct', hue='birth_sex', data=self.opp.rename(columns={
            'sex': 'birth_sex'}), palette='dark')
        fig = plot.get_figure()
        fig.autofmt_xdate()
        fig.set_size_inches(12, 8)
        fig.suptitle('Percentage of births accounted for by opposite-gendered names, 1900 to latest')
        fig.savefig('img/opposite.png')

    def create_markdown_tables(self):
        df = self.summary.copy()
        year_min = df.year.min()
        year_max = df.year.max()
        df.pct = df.pct.apply(lambda x: round(x, 3))
        text = [
            f'**Year: {year_min}**',
            df[df.year == year_min].to_markdown(index=False),
            f'**Year: {year_max}**',
            df[df.year == year_max].to_markdown(index=False),
        ]
        open('markdown_table.txt', 'w').write('\n\n'.join(text))


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
