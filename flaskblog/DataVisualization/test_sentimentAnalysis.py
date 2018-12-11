from unittest import TestCase
import pandas as pd
from flaskblog.DataVisualization import sentimentAnalysis


class TestSentimentAnalysis(TestCase):
    def test_percentage(self):
        senti = sentimentAnalysis.SentimentAnalysis()
        num, den = 10, 100
        percFn = senti.percentage(num, den)
        perc = 100 * num / den
        self.assertEqual(perc, percFn)

    def test_polarity_analysis(self):
        texts = ["'Good'", "'Bad'", "'India'"]
        for t in texts:
            df = pd.DataFrame([t], columns=["tweets"])
            senti = sentimentAnalysis.SentimentAnalysis()
            if t == "'Good'":
                self.assertEqual("Positive", senti.polarity_analysis(df))
            elif t == "'Bad'":
                self.assertEqual("Negative", senti.polarity_analysis(df))
            elif t == "'India'":
                self.assertEqual("Neutral", senti.polarity_analysis(df))
