
import pickle
from pathlib import Path

from sklearn.linear_model import LogisticRegression
import polars as pl


filename = Path(__file__).parent / 'penguins.csv'
df = pl.read_csv(filename)
df = df.drop_nulls()

# train-test-split, scaling, overfitting are all ignored here
X = df[["bill_length_mm", "body_mass_g"]]
y = df["species"]

model = LogisticRegression()
model.fit(X, y)
print(model.score(X, y))

pickle.dump(model, open("model.pkl", "wb"))
