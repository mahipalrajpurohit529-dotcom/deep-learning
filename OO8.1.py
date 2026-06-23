"""
review_sentiment_pipeline.py

A small, deployable pipeline that takes a CSV file containing a single
column of raw review text, cleans the text, classifies the sentiment of
each review, and exports the result to a new CSV file.

Usage (command line):
    python review_sentiment_pipeline.py reviews.csv -o reviews_with_sentiment.csv

Usage (as a library, e.g. inside a web app):
    from review_sentiment_pipeline import ReviewSentimentAnalyzer

    analyzer = ReviewSentimentAnalyzer()
    output_path = analyzer.run("reviews.csv", "reviews_with_sentiment.csv")
"""

import re
import string
import argparse

import pandas as pd
from textblob import TextBlob


class ReviewSentimentAnalyzer:
    """
    End-to-end pipeline: load -> clean -> classify sentiment -> export.

    The class is built so each stage can also be called on its own
    (useful if you later want to plug this into a Flask/FastAPI/Streamlit
    app and only need one piece, e.g. just the cleaning step).
    """

    def __init__(self, text_column: str | None = None):
        """
        Parameters
        ----------
        text_column : str, optional
            Name of the column that holds the review text. If not given,
            the first column of the uploaded CSV is used automatically,
            so the user doesn't need to know/match a specific header name.
        """
        self.text_column = text_column
        self.df: pd.DataFrame | None = None

    # ------------------------------------------------------------------
    # 1. Load
    # ------------------------------------------------------------------
    def load_csv(self, input_path: str) -> "ReviewSentimentAnalyzer":
        """Read the uploaded CSV into a DataFrame."""
        df = pd.read_csv(input_path)

        if df.shape[1] == 0:
            raise ValueError("The CSV file has no columns.")

        # If the user didn't specify a column, just take the first one --
        # this matches the "one column of reviews" use case.
        if self.text_column is None:
            self.text_column = df.columns[0]

        if self.text_column not in df.columns:
            raise ValueError(
                f"Column '{self.text_column}' not found. "
                f"Available columns: {list(df.columns)}"
            )

        df[self.text_column] = df[self.text_column].astype(str)
        self.df = df
        return self

    # ------------------------------------------------------------------
    # 2. Clean
    # ------------------------------------------------------------------
    @staticmethod
    def _remove_html_tags(text: str) -> str:
        return re.sub(r"<.*?>", "", text)

    @staticmethod
    def _remove_url(text: str) -> str:
        return re.sub(r"https?://\S+|www\.\S+", "", text)

    @staticmethod
    def _remove_punctuation(text: str) -> str:
        return text.translate(str.maketrans("", "", string.punctuation))

    def clean_text(self, text: str) -> str:
        """Apply all cleaning steps to a single piece of text."""
        text = self._remove_html_tags(text)
        text = self._remove_url(text)
        text = self._remove_punctuation(text)
        return text.strip()

    def clean(self) -> "ReviewSentimentAnalyzer":
        """Clean the text column for the whole DataFrame."""
        if self.df is None:
            raise RuntimeError("No data loaded. Call load_csv() first.")
        self.df[self.text_column] = self.df[self.text_column].apply(self.clean_text)
        return self

    # ------------------------------------------------------------------
    # 3. Sentiment
    # ------------------------------------------------------------------
    @staticmethod
    def _classify_sentiment(text: str) -> str:
        polarity = TextBlob(text).sentiment.polarity
        if polarity > 0.1:
            return "Positive"
        elif polarity < -0.1:
            return "Negative"
        return "Neutral"

    def analyze_sentiment(self) -> "ReviewSentimentAnalyzer":
        """Add a 'sentiment' column based on the (cleaned) text column."""
        if self.df is None:
            raise RuntimeError("No data loaded. Call load_csv() first.")
        self.df["sentiment"] = self.df[self.text_column].apply(self._classify_sentiment)
        return self

    # ------------------------------------------------------------------
    # 4. Export
    # ------------------------------------------------------------------
    def export(self, output_path: str) -> str:
        """Write the cleaned, classified DataFrame out to CSV."""
        if self.df is None:
            raise RuntimeError("Nothing to export yet. Run the pipeline first.")
        self.df.to_csv(output_path, index=False)
        return output_path

    # ------------------------------------------------------------------
    # Convenience: run the whole pipeline in one call
    # ------------------------------------------------------------------
    def run(self, input_path: str, output_path: str) -> str:
        """Load -> clean -> classify -> export, in one call. Returns the output path."""
        self.load_csv(input_path)
        self.clean()
        self.analyze_sentiment()
        return self.export(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Clean review text from a CSV and classify each review's sentiment."
    )
    parser.add_argument("input_csv", help="Path to the input CSV (one column of reviews).")
    parser.add_argument(
        "-o", "--output",
        default="reviews_with_sentiment.csv",
        help="Path to write the cleaned + classified CSV (default: reviews_with_sentiment.csv).",
    )
    parser.add_argument(
        "-c", "--column",
        default=None,
        help="Name of the text column, if your CSV has a header you want to target. "
             "Defaults to the first column.",
    )
    args = parser.parse_args()

    analyzer = ReviewSentimentAnalyzer(text_column=args.column)
    output_path = analyzer.run(args.input_csv, args.output)
    print(f"Done. {len(analyzer.df)} reviews processed.")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    analyzer = ReviewSentimentAnalyzer()
    output_path = analyzer.run(
        r"C:\codings\datasets\noisy_text_dataset_100_rows.csv",
        r"C:\codings\datasets\noisy_text_dataset_100_rows_sentiment.csv"
    )
    print(f"Done. {len(analyzer.df)} reviews processed.")
    print(f"Results saved to: {output_path}")
    print(analyzer.df.head())