from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn import run as app_run

from src.constants import APP_HOST, APP_PORT
from src.pipline.prediction_pipeline import (
    VehicleData,
    VehicleDataClassifier,
)
from src.pipline.training_pipeline import TrainPipeline



BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"



app = FastAPI(
    title="Vehicle Insurance Prediction",
    description="Vehicle insurance customer response prediction",
    version="1.0.0",
)



if STATIC_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



class DataForm:
    def __init__(self, request: Request):
        self.request = request

        self.Gender: Optional[int] = None
        self.Age: Optional[int] = None
        self.Driving_License: Optional[int] = None
        self.Region_Code: Optional[float] = None
        self.Previously_Insured: Optional[int] = None
        self.Annual_Premium: Optional[float] = None
        self.Policy_Sales_Channel: Optional[float] = None
        self.Vintage: Optional[int] = None
        self.Vehicle_Age_lt_1_Year: Optional[int] = None
        self.Vehicle_Age_gt_2_Years: Optional[int] = None
        self.Vehicle_Damage_Yes: Optional[int] = None

    async def get_vehicle_data(self):
        form = await self.request.form()

        
        self.Gender = int(form.get("Gender"))
        self.Age = int(form.get("Age"))
        self.Driving_License = int(
            form.get("Driving_License")
        )
        self.Previously_Insured = int(
            form.get("Previously_Insured")
        )
        self.Vintage = int(form.get("Vintage"))
        self.Vehicle_Age_lt_1_Year = int(
            form.get("Vehicle_Age_lt_1_Year")
        )
        self.Vehicle_Age_gt_2_Years = int(
            form.get("Vehicle_Age_gt_2_Years")
        )
        self.Vehicle_Damage_Yes = int(
            form.get("Vehicle_Damage_Yes")
        )

        # Floating-point fields
        self.Region_Code = float(form.get("Region_Code"))
        self.Annual_Premium = float(
            form.get("Annual_Premium")
        )
        self.Policy_Sales_Channel = float(
            form.get("Policy_Sales_Channel")
        )



@app.get("/", response_class=HTMLResponse, tags=["prediction"])
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="vehicledata.html",
        context={
            "context": None,
            "prediction": None,
            "error": None,
        },
    )



@app.get("/train", tags=["training"])
async def train_route_client():
    try:
        train_pipeline = TrainPipeline()
        train_pipeline.run_pipeline()

        return {
            "status": True,
            "message": "Training completed successfully!",
        }

    except Exception as e:
        return Response(
            content=f"Training failed: {str(e)}",
            status_code=500,
            media_type="text/plain",
        )



@app.post("/", response_class=HTMLResponse, tags=["prediction"])
async def predict_route_client(request: Request):
    try:
        
        form = DataForm(request)
        await form.get_vehicle_data()

        
        vehicle_data = VehicleData(
            Gender=form.Gender,
            Age=form.Age,
            Driving_License=form.Driving_License,
            Region_Code=form.Region_Code,
            Previously_Insured=form.Previously_Insured,
            Annual_Premium=form.Annual_Premium,
            Policy_Sales_Channel=form.Policy_Sales_Channel,
            Vintage=form.Vintage,
            Vehicle_Age_lt_1_Year=form.Vehicle_Age_lt_1_Year,
            Vehicle_Age_gt_2_Years=form.Vehicle_Age_gt_2_Years,
            Vehicle_Damage_Yes=form.Vehicle_Damage_Yes,
        )

        
        vehicle_df = vehicle_data.get_vehicle_input_data_frame()

      
        model_predictor = VehicleDataClassifier()
        value = model_predictor.predict(dataframe=vehicle_df)[0]

       
        status = (
            "Response-Yes"
            if int(value) == 1
            else "Response-No"
        )

   
        return templates.TemplateResponse(
            request=request,
            name="vehicledata.html",
            context={
                "context": status,
                "prediction": status,
                "error": None,
            },
        )

    except (TypeError, ValueError) as e:
        return templates.TemplateResponse(
            request=request,
            name="vehicledata.html",
            context={
                "context": None,
                "prediction": None,
                "error": f"Invalid form input: {str(e)}",
            },
            status_code=400,
        )

    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="vehicledata.html",
            context={
                "context": None,
                "prediction": None,
                "error": f"Prediction failed: {str(e)}",
            },
            status_code=500,
        )


# --------------------------------------------------
# Application entry point
# --------------------------------------------------

if __name__ == "__main__":
    app_run(
        app,
        host=APP_HOST,
        port=APP_PORT,
    )
