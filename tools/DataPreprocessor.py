import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
from sklearn import set_config


class DataPreprocessor:
    """
    A class to preprocess datasets for machine learning tasks.

    Attributes
    ----------
    df : pd.DataFrame
        The dataset to be processed.
    pipeline : sklearn.pipeline.Pipeline
        The pipeline to process the dataset.

    Methods
    -------
    split_data(test_size=0.2, random_state=None):
        Splits the dataset into train and test sets.

    remove_target(target_column):
        Removes the target column from the dataset.

    create_pipeline(numeric_transformers, categorical_transformers, final_transformers=None):
        Creates a preprocessing pipeline for the dataset.

    fit_transform(X_train, y_train):
        Fits and transforms the train set using the pipeline.

    transform(X_test):
        Transforms the test set using the fitted pipeline.

    visualize_pipeline():
        Visualizes the pipeline structure.
    """

    def __init__(self, df):
        """
        Constructs all the necessary attributes for the DataPreprocessor object.

        Parameters
        ----------
        df : pd.DataFrame
            The dataset to be processed.
        """
        self.df = df
        self.pipeline = None
        self.numeric_features = None
        self.categorical_features = None

    def split_data(self, target_column, test_size=0.2, random_state=None, split=True):
        """
        Splits the dataset into train and test sets, or only into features and target.

        Parameters
        ----------
        target_column : str
            The target column name.
        test_size : float, optional
            The proportion of the dataset to include in the test split (default is 0.2).
        random_state : int, optional
            The random state for reproducibility (default is None).
        split : bool, optional
            Whether to split into train/test sets (default is True).

        Returns
        -------
        If split is True:
            X_train : pd.DataFrame
                Training data without the target column.
            X_test : pd.DataFrame
                Testing data without the target column.
            y_train : pd.Series
                Target values for the training data.
            y_test : pd.Series
                Target values for the testing data.
        If split is False:
            X : pd.DataFrame
                Data without the target column.
            y : pd.Series
                Target values.
        """
        X = self.df.drop(columns=[target_column])
        y = self.df[target_column]

        if split:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            return X_train, X_test, y_train, y_test
        else:
            return X, y

    def initialize_features(self, X):
        """
        Initializes the numeric and categorical feature lists based on the given DataFrame.

        Parameters
        ----------
        X : pd.DataFrame
            The DataFrame to analyze for features.
        """
        self.numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_features = X.select_dtypes(
            include=[object, "category"]
        ).columns.tolist()

    def remove_target(self, target_column):
        """
        Removes the target column from the dataset.

        Parameters
        ----------
        target_column : str
            The target column name.

        Returns
        -------
        pd.DataFrame
            The dataset without the target column.
        """
        return self.df.drop(columns=[target_column])

    def create_pipeline(
        self, numeric_transformers, categorical_transformers, final_transformers=None
    ):
        """
        Creates a preprocessing pipeline for the dataset.

        Parameters
        ----------
        numeric_transformers : list
            List of transformers for numeric features.
        categorical_transformers : list
            List of transformers for categorical features.
        final_transformers : list, optional
            List of final transformers to apply to the combined dataset (default is None).
        """
        numeric_pipeline = Pipeline(steps=numeric_transformers).set_output(
            transform="pandas"
        )
        if categorical_transformers:
            categorical_pipeline = Pipeline(steps=categorical_transformers).set_output(
                transform="pandas"
            )
        else:
            categorical_pipeline = "drop"

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_pipeline, self.numeric_features),
                ("cat", categorical_pipeline, self.categorical_features),
            ]
        )

        if final_transformers:
            final_pipeline = Pipeline(
                steps=[("preprocessor", preprocessor)] + final_transformers
            ).set_output(transform="pandas")
            self.pipeline = final_pipeline
        else:
            self.pipeline = Pipeline(steps=[("preprocessor", preprocessor)])

    def fit_transform(self, X_train, y_train=None):
        """
        Fits and transforms the train set using the pipeline.

        Parameters
        ----------
        X_train : pd.DataFrame
            Training data without the target column.
        y_train : pd.Series, optional
            Target values for the training data.

        Returns
        -------
        pd.DataFrame
            Transformed training data.
        """
        if y_train is not None:
            return self.pipeline.fit_transform(X_train, y_train)
        else:
            return self.pipeline.fit_transform(X_train)

    def transform(self, X_test):
        """
        Transforms the test set using the fitted pipeline.

        Parameters
        ----------
        X_test : pd.DataFrame
            Testing data without the target column.

        Returns
        -------
        np.ndarray
            Transformed testing data.
        """
        return self.pipeline.transform(X_test)

    def visualize_pipeline(self):
        """
        Visualizes the pipeline structure.
        """
        set_config(display="diagram")
        return self.pipeline
