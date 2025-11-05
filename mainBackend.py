from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pandas as pd
from typing import List, Dict, Any

app = FastAPI(title="Data Analyzer")

class DataInput(BaseModel):
    data: List[Dict]
    column: str
class Dataonly(BaseModel):
    data:List[Dict[str, Any]]


@app.get("/")
def greet():
    return {"message":"Welcome to Data Analyzer"}

@app.post("/summary")
def summary_stats(data_input:DataInput):
    df = pd.DataFrame(data_input.data)
    col = data_input.column

    if col not in df.columns:
        return {"error":f"Column {col} Not Found"}

    values = df[col].dropna().astype(float)
    return {
            "column":col,
            "count":len(values),
            "mean":float(np.mean(values)),
            "median":float(np.median(values)),
            "variance":float(np.var(values)),
            "std_dev": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values))
    }

@app.post("/missing")
def missing_values(data_input: DataInput):
    df = pd.DataFrame(data_input.data)
    missing = df.isna().sum().to_dict()
    return {"missing_values":missing}

@app.post("/correlation")
def correlation_matrix(data_input: Dataonly):
    try:
        df = pd.DataFrame(data_input.data)
        correlation = df.corr().round(3).to_dict()
        return {"correlation": correlation}
    except Exception as e:
        return {"error": str(e)}