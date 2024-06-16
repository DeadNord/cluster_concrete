from sklearn.model_selection import GridSearchCV
from sklearn.metrics import silhouette_score
from sklearn import set_config
import pandas as pd
from IPython.display import display
from sklearn.metrics import davies_bouldin_score, calinski_harabasz_score


class ModelPipeline:
    """
    A class to create and train model pipelines with grid search for hyperparameter tuning.

    Attributes
    ----------
    best_models : dict
        Dictionary of best models found by grid search for each model.
    best_params : dict
        Dictionary of best hyperparameters found by grid search for each model.
    best_scores : dict
        Dictionary of best scores achieved by grid search for each model.
    best_model_name : str
        Name of the best model based on the evaluation score.

    Methods
    -------
    train(X_train, pipelines, param_grids, scoring='silhouette_score', cv=5):
        Trains the pipelines with grid search.

    display_results():
        Displays the best parameters and evaluation metrics.

    visualize_pipeline(model_name):
        Visualizes the pipeline structure for a given model.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the ModelPipeline object.
        """
        self.best_models = {}
        self.best_params = {}
        self.best_scores = {}
        self.best_model_name = None

    def train(
        self,
        X_train,
        pipelines,
        param_grids,
        scoring="silhouette_score",
        cv=5,
    ):
        """
        Trains the pipelines with grid search.

        Parameters
        ----------
        X_train : pd.DataFrame
            Training data.
        pipelines : dict
            Dictionary of model pipelines.
        param_grids : dict
            Dictionary of hyperparameter grids for grid search.
        scoring : str, optional
            Scoring metric for grid search (default is 'silhouette_score').
        cv : int, optional
            Number of cross-validation folds (default is 5).
        """
        for model_name, pipeline in pipelines.items():
            grid_search = GridSearchCV(
                pipeline,
                param_grids[model_name],
                cv=cv,
                scoring=(
                    self._silhouette_scorer
                    if scoring == "silhouette_score"
                    else scoring
                ),
            )

            grid_search.fit(X_train)

            self.best_models[model_name] = grid_search.best_estimator_
            self.best_params[model_name] = grid_search.best_params_
            self.best_scores[model_name] = grid_search.best_score_

            # Update the best model name based on the score
            if (
                self.best_model_name is None
                or self.best_scores[model_name] > self.best_scores[self.best_model_name]
            ):
                self.best_model_name = model_name

    def _silhouette_scorer(self, estimator, X):
        cluster_labels = estimator.fit_predict(X)
        return silhouette_score(X, cluster_labels)

    def display_results(self, X_train, help_text=False):
        """
        Displays the best parameters and evaluation metrics.

        Parameters
        ----------
        X_train : pd.DataFrame
            The training data.
        help_text : bool, optional
            Whether to display the help text for interpreting the metrics (default is False).
        """
        silhouette_scores = []
        davies_bouldin_scores = []
        calinski_harabasz_scores = []

        for model_name in self.best_models.keys():
            best_model = self.best_models[model_name]
            cluster_labels = best_model.predict(X_train)

            silhouette = silhouette_score(X_train, cluster_labels)
            davies_bouldin = davies_bouldin_score(X_train, cluster_labels)
            calinski_harabasz = calinski_harabasz_score(X_train, cluster_labels)

            silhouette_scores.append(silhouette)
            davies_bouldin_scores.append(davies_bouldin)
            calinski_harabasz_scores.append(calinski_harabasz)

        results_df = pd.DataFrame(
            {
                "Model": list(self.best_models.keys()),
                "Silhouette Score": silhouette_scores,
                "Davies-Bouldin Index": davies_bouldin_scores,
                "Calinski-Harabasz Index": calinski_harabasz_scores,
                "Best Parameters": [
                    self.best_params[model_name]
                    for model_name in self.best_models.keys()
                ],
            }
        )

        print("Evaluation Metrics for Best Models:")
        display(results_df)

        if help_text:
            print("\nMetric Explanations:")
            print(
                "Silhouette Score: Measures how similar an object is to its own cluster compared to other clusters."
            )
            print("  - Range: [-1, 1], higher is better.")
            print("  - Higher values indicate better-defined clusters.")
            print(
                "Davies-Bouldin Index: Measures the average similarity ratio of each cluster with its most similar cluster."
            )
            print("  - Range: [0, ∞), lower is better.")
            print("  - Lower values indicate better clustering.")
            print(
                "Calinski-Harabasz Index: Ratio of the sum of between-cluster dispersion to within-cluster dispersion."
            )
            print("  - Range: [0, ∞), higher is better.")
            print("  - Higher values indicate better-defined clusters.")

    def visualize_pipeline(self, model_name):
        """
        Visualizes the pipeline structure for a given model.

        Parameters
        ----------
        model_name : str
            Name of the model to visualize.
        """
        set_config(display="diagram")
        return self.best_models[model_name]

    def generate_cluster_report(self, df_original, df_transformed):
        """
        Generates a report with descriptive statistics for each cluster.

        Parameters
        ----------
        df_original : pd.DataFrame
            The original dataset.
        df_transformed : pd.DataFrame
            The transformed dataset used for clustering.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing median values for each feature and the count of objects in each cluster.
        """
        best_kmeans = self.best_models["KMeans"]
        df_original["Cluster"] = best_kmeans.predict(df_transformed)

        # Calculate medians and counts for each cluster
        cluster_report = df_original.groupby("Cluster").median()
        cluster_report["Count"] = df_original["Cluster"].value_counts()

        return cluster_report


# # Пример использования:
# from sklearn.preprocessing import StandardScaler
# from sklearn.pipeline import Pipeline
# from sklearn.cluster import KMeans

# # Пример данных
# data = {
#     "Cement": [540.0, 540.0, 332.5, 332.5, 198.6],
#     "BlastFurnaceSlag": [0.0, 0.0, 142.5, 142.5, 132.4],
#     "FlyAsh": [0.0, 0.0, 0.0, 0.0, 0.0],
#     "Water": [162.0, 162.0, 228.0, 228.0, 192.0],
#     "Superplasticizer": [2.5, 2.5, 0.0, 0.0, 0.0],
#     "CoarseAggregate": [1040.0, 1055.0, 932.0, 932.0, 978.4],
#     "FineAggregate": [676.0, 676.0, 594.0, 594.0, 825.5],
#     "Age": [28, 28, 270, 365, 360],
#     "CompressiveStrength": [79.99, 61.89, 40.27, 41.05, 44.30],
# }

# df = pd.DataFrame(data)

# # Нормализация данных
# scaler = StandardScaler()
# df_scaled = scaler.fit_transform(df)

# # Определение pipeline для KMeans
# pipelines = {
#     "KMeans": Pipeline(
#         [
#             ("cluster", KMeans(random_state=42)),
#         ]
#     ),
# }

# # Определение гиперпараметров для KMeans
# param_grids = {
#     "KMeans": {
#         "cluster__n_clusters": [2, 3, 4, 5, 6, 7, 8, 9, 10],
#     },
# }

# # Инициализация и обучение ModelPipeline
# model_pipeline = ModelPipeline()
# model_pipeline.train(df_scaled, pipelines, param_grids)

# # Отображение результатов
# model_pipeline.display_results()

# # Получение меток кластеров
# best_kmeans = model_pipeline.best_models["KMeans"]
# df["Cluster"] = best_kmeans.predict(df_scaled)

# # Вывод результатов
# print(df)