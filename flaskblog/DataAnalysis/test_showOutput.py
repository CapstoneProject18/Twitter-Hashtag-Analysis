from unittest import TestCase
import pandas as pd
from flaskblog.DataAnalysis import show_output


class TestShowOutput(TestCase):
    def test_print_output(self):
        df = pd.DataFrame([["Rishabh", "Tweets_text"]], columns=["username", "tweets"])
        s = show_output.ShowOutput()
        total, people = s.print_output(df)
        self.assertEqual("1", total)
