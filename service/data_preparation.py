import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy import stats
from conf.settings import FilesConf, ModelConf, DatabaseConf
from conf.settings import CONNECTION_STRING
from sqlalchemy import create_engine
from statsmodels.tsa.stattools import pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.preprocessing import LabelEncoder, OneHotEncoder



MONTHS = {
        "Enero": 1,
        "Febrero": 2,
        "Marzo": 3,
        "Abril": 4,
        "Mayo": 5,
        "Junio": 6,
        "Julio": 7,
        "Agosto": 8,
        "Septiembre": 9,
        "Octubre": 10,
        "Noviembre": 11,
        "Diciembre": 12,
    }

DEFAULT_SPLIT = {
    "train": ModelConf.splits.train,
    "test": ModelConf.splits.test,
    "validate": ModelConf.splits.validate
}

MAX_LAGS = ModelConf.lags.max_lags
MIN_LAG = ModelConf.lags.min_lags

ALPHA = ModelConf.lags.alpha


class DataSets(object):

    functions = {
        "log": lambda x: np.log(x),
        "root_2": lambda x: np.sqrt(x),
        "root_5": lambda x: np.power(x, 1 / 5),
        "root_7": lambda x: np.power(x, 1 / 7)
    }

    response_function = {
        "identity": lambda x: x,
        "log": lambda x: np.log(x),
        "root_2": lambda x: np.sqrt(x),
        "root_5": lambda x: np.power(x, 1 / 5),
        "root_7": lambda x: np.power(x, 1/7)
    }

    inverse_function = {
        "identity": (lambda x: x),
        "log": lambda x: np.exp(x),
        "root_2": lambda x: np.power(x, 2),
        "root_5": lambda x: np.power(x, 5),
        "root_7": lambda x: np.power(x, 7)
    }

    def __init__(self, data, split_vals=DEFAULT_SPLIT, encode_string=True,
                 one_hot_encode=True, categ_to_num=False,
                 predictive_var="value", link="identity",
                 transformations={}, shuffle=False):
        self.shuffle = shuffle
        self._train_reference = split_vals["train"]
        self._test_validate_reference = split_vals["train"] + split_vals["test"]
        data[predictive_var] = self.response_function[link](data[predictive_var].values.astype(np.float))
        if transformations:
            for col in transformations:
                if col not in data.columns:
                    continue
                data[col] = self.functions[transformations[col]](data[col].values.astype(np.float))
        self.link = link
        self.predictive_var = predictive_var
        self.transformations = transformations
        self.one_hot_encode = one_hot_encode
        self.string_encoder = {}
        self.one_hot_encoder = {}
        self.string_cols = None
        self.category_encoder = {}
        self.data = data.reset_index(drop=True)
        self.shuffle_index = self.data.sample(frac=1).index
        self.encode_string_required = encode_string
        self.categ_to_num_required = categ_to_num
        if encode_string:
            self._encode_string()
        elif categ_to_num:
            self.category_to_numeric()
        self.n, self.m = data.shape
        self._split_data()

    def _split_data(self):
        df = self.data.loc[self.shuffle_index] if self.shuffle else self.data
        n = len(self.data)
        self.train, self.test, self.validate = np.split(
            df,
            [int(n * self._train_reference), int(n * self._test_validate_reference)])

    def get_train(self, output_var=False, apply_inverse=False):
        if output_var:
            if apply_inverse:
                return self.inverse_function[self.link](self.train[self.predictive_var].values)
            return self.train[self.predictive_var].values
        return self.train[self.train.columns[self.train.columns != self.predictive_var]]

    def get_test(self, output_var=False, apply_inverse=False):
        if output_var:
            if apply_inverse:
                return self.inverse_function[self.link](self.test[self.predictive_var].values)
            return self.test[self.predictive_var].values
        return self.test[self.test.columns[self.test.columns != self.predictive_var]]

    def get_validate(self, output_var=False, apply_inverse=False):
        if output_var:
            if apply_inverse:
                return self.inverse_function[self.link](self.validate[self.predictive_var].values)
            return self.validate[self.predictive_var].values
        return self.validate[self.validate.columns[self.validate.columns != self.predictive_var]]

    def category_to_numeric(self):
        self.string_cols = self.data.dtypes.to_frame()[(self.data.dtypes.to_frame() == 'object').values].index.values
        self._split_data()
        for col in self.string_cols:
            self.category_encoder[col] = self.train.groupby(col).value.mean().to_dict()
            self.data[col] = self.data[col].replace(self.category_encoder[col])

    def _encode_string(self):
        sub_data = self.data[self.data.columns[self.data.columns != self.predictive_var]]
        self.string_cols = sub_data.dtypes.to_frame()[(sub_data.dtypes.to_frame() == 'object').values].index.values
        for col in self.string_cols:
            LE = LabelEncoder()
            LE.fit(sub_data[col])
            classes = [col + "_" + str(i) for i in range(len(LE.classes_))]
            self.string_encoder[col] = LE
            self.data[col] = LE.transform(self.data[col])
            if self.one_hot_encode:
                OHE = OneHotEncoder()
                OHE.fit(self.data[col].values.reshape(-1, 1))
                vals = OHE.fit_transform(self.data[col].values.reshape(-1, 1)).toarray()
                temp = pd.DataFrame(vals, columns=classes)
                self.data = pd.concat([self.data, temp], axis=1)
                del self.data[col]
                self.one_hot_encoder[col] = OHE

    def external(self, df, output_var=False, apply_inverse=False):
        if output_var:
            if apply_inverse:
                return df[self.predictive_var].values
            return self.response_function[self.link](df[self.predictive_var].values.astype(np.float))
        if self.transformations:
            for col in self.transformations:
                if col not in self.data.columns:
                    continue
                df[col] = self.functions[self.transformations[col]](df[col].values.astype(np.float))
        df = df.reset_index(drop=True)
        for col in self.string_cols:
            if self.encode_string_required:
                LE = self.string_encoder[col]
                classes = [col + "_" + str(i) for i in range(len(LE.classes_))]
                df[col] = LE.transform(df[col])
                if self.one_hot_encode:
                    OHE = self.one_hot_encoder[col]
                    vals = OHE.fit_transform(df[col].values.reshape(-1, 1)).toarray()
                    temp = pd.DataFrame(vals, columns=classes)
                    df = pd.concat([df, temp], axis=1)
                    del df[col]
            elif self.categ_to_num_required:
                df[col] = df[col].replace(self.category_encoder[col])

        return df[df.columns[df.columns != self.predictive_var]]


def has_month(string):
    for month in MONTHS:
        if month.lower() in string.lower():
            return True
    return False


def optimize_lags(time_series_vector, plot=False, max_lags=None, min_lag=None):
    max_lags = max_lags if max_lags else MAX_LAGS
    min_lag = min_lag if min_lag else MIN_LAG

    def is_significant(value, threshold):
        return (value <= -threshold) or (value >= threshold)

    def confident_lags(pacf_vector, threshold):
        compare_zip = zip(map(lambda x: is_significant(x, threshold), pacf_vector),
                          range(len(pacf_vect)))
        return [val[1] for val in compare_zip if val[0] and val[1] > min_lag]

    significance_threshold = stats.norm.ppf(1 - ALPHA) / np.sqrt(len(time_series_vector))
    if plot:
        plot_acf(time_series_vector, lags=max_lags)
        plot_pacf(time_series_vector, lags=max_lags)
    pacf_vect = pacf(time_series_vector, nlags=max_lags)
    lags = confident_lags(pacf_vect, significance_threshold)
    return lags


def suggested_lags(df, cols, frequency=0.05, plot=False, min_lag=0):

    def get_by_recursive_combinations(df, cols, n_lags=[]):
        unique_vals = df[cols[0]].unique()
        for val in unique_vals:
            sub_df = df.query("{} == '{}'".format(cols[0], val))
            if sub_df.value.std() < 1:
                continue
            n_lags += (optimize_lags(sub_df.value, min_lag=min_lag) if len(cols)==1 else get_by_recursive_combinations(
                sub_df, cols[1:], n_lags=[]))
        return list(filter(lambda x: x > 0, n_lags))

    n_lags = get_by_recursive_combinations(df, cols, n_lags=[])
    n, unique_lags = len(n_lags), np.unique(n_lags)
    freq_lags = [len(list(filter(lambda x: x == u, n_lags))) / n for u in unique_lags]
    lag_df = pd.DataFrame({"lag": unique_lags, "freq": freq_lags})
    if plot:
        lag_df.plot.bar(x="lag", y="freq")
        plt.ylabel("Frequency")
        plt.title("Suggested lags frequency")
    suggested = lag_df.query("freq > {}".format(frequency)).lag.values
    return [val for val in suggested if val < MAX_LAGS]


def add_lags(sub_df, lags):
    original_index = sub_df.index
    response = sub_df.reset_index(drop=True)[["value"]]
    for lag in lags:
        temp = response[["value"]].iloc[:-lag]
        temp.index = temp.index + lag
        response["t-{}".format(lag)] = temp
    response.index = original_index
    del response["value"]
    return pd.concat([sub_df, response], axis=1)


def add_lags_recursive(df, cols, lags, result_df=pd.DataFrame([])):
    unique_vals = df[cols[0]].unique()
    for val in unique_vals:
        sub_df = df.query("{} == '{}'".format(cols[0], val))
        result_df = pd.concat([result_df, add_lags(sub_df, lags)], axis=0) \
            if len(cols) == 1 else add_lags_recursive(sub_df, cols[1:], lags, result_df=result_df)
    return result_df


def get_data(min_lag=0, save=True, read=True):
    if os.path.exists(FilesConf.FileNames.data) and read:
        df = pd.read_pickle(FilesConf.FileNames.data)
        base_cols = [c for c in df.columns.values if "t-" not in str(c)]
        temporal_validation = pd.read_pickle(FilesConf.FileNames.validation)
        # LAGS
        cols = ["economic_division", "age_range", "gender"]
        lags = suggested_lags(df, cols, frequency=0.05, min_lag=min_lag)
        cs = list(set(df.columns.tolist()).intersection(["t-" + str(lg) for lg in lags]))
        return df[base_cols + cs], temporal_validation[base_cols + cs], lags
    engine = create_engine(DatabaseConf.connection_string)
    col_names = {
        "division_economica": "economic_division",
        "genero": "gender",
        "edad": "age_range",
        "ta": "value",
        "etiqueta_mes": "variable"
    }
    df = pd.read_sql_query(DatabaseConf.query_string, con=engine)
    del df["fecha"]
    df = df.rename(columns=col_names)
    df["year"], df["month"] = df.variable.str.split("/").str
    df["month"] = df["month"].replace(MONTHS)
    df["year"] = df["year"].values.astype(np.float)
    del df["variable"]
    df = df.query("value != 'N/D'").reset_index(drop=True)
    df["value"] = df.value.values.astype(np.float)
    df["time"] = (df.year + (df.month-1) / 12).values
    # LAGS
    cols = ["economic_division", "age_range", "gender"]
    lags = suggested_lags(df, cols, frequency=0.05, min_lag=min_lag)
    df = add_lags_recursive(df, cols, lags).sort_index().dropna()
    # Temporal validation
    temporal_validation = df.query("time >= 2017").sort_values("time").reset_index(drop=True)
    df = df.query("time < 2017").sort_values("time").reset_index(drop=True)
    del df["time"]
    del temporal_validation["time"]
    if save:
        df.to_pickle(FilesConf.FileNames.data)
        temporal_validation.to_pickle(FilesConf.FileNames.validation)
    return df, temporal_validation, lags
