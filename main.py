from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
import pandas as pd
from prophet import Prophet
import uvicorn

# Manually define the FastAPI app and override docs URL
app = FastAPI(docs_url="/docs")

# ✅ Custom Swagger UI at /docs
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="PrimePredict API Docs")

# ✅ Root welcome route
@app.get("/")
def root():
    return {"message": "Welcome to PrimePredict API. Visit /docs to test."}

# ✅ Request model
class ForecastRequest(BaseModel):
    product_id: str
    historical_data: list
    periods: int

# ✅ Forecast route
@app.post("/forecast")
def forecast(request: ForecastRequest):
    try:
        df = pd.DataFrame(request.historical_data)
        model = Prophet()
        model.fit(df)

        future = model.make_future_dataframe(periods=request.periods)
        forecast = model.predict(future)
        result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(request.periods).to_dict(orient="records")
        
        return {"product_id": request.product_id, "forecast": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Run app
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)