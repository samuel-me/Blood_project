## Flask 
import pickle 
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify


app = Flask(__name__)

#load the model and scaler 

with open('logistics_model.pkl', 'rb') as file:
  model = pickle.load(file)

with open('standard_scaler.pkl', 'rb') as file:
  scaler = pickle.load(file)


@app.route("/")
def home():
  return "hello, i am alive"

@app.route("/predict", methods=["POST"])
def predict():
  try: 
    data = request.get_json()

    input_data = pd.DataFrame([data])

    if not data:
      return jsonify({"error": "data not provided"}), 400


    required_columns = ['as_of_month', 'months_since_joined', 'recency_months',
        'frequency_total_donations', 'eligible_this_month']

    if not all (col in input_data.columns for col in required_columns):
      return jsonify({"error": "Required column: {required_columns}"}), 400
    

    ## scale
    scaled_data = scaler.transform(input_data)


    #make prediction 
    pred = model.predict_proba(scaled_data)

    #response 
    response = {
        "prediction": float(pred[0][1])
    }

    return jsonify(response)

  except Exception as e:
    return jsonify({"error": str(e)}), 500

if __name__ == "main":
  app.run(debug = True)
