# Import necessary libraries
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
superkart_sales_predictor_api = Flask("SuperKart Sales Predictor")

# Load the trained machine learning model (preprocessing + regressor pipeline)
model = joblib.load("superkart_sales_prediction_model_v1_0.joblib")

# Define a route for the home page (GET request)
@superkart_sales_predictor_api.get('/')
def home():
    """
    This function handles GET requests to the root URL ('/') of the API.
    It returns a simple welcome message.
    """
    return "Welcome to the SuperKart Sales Prediction API!"

# Define an endpoint for single product/store prediction (POST request)
@superkart_sales_predictor_api.post('/v1/superkart')
def predict_sales():
    """
    This function handles POST requests to the '/v1/superkart' endpoint.
    It expects a JSON payload containing product and store details and
    returns the predicted sales total as a JSON response.
    """
    # Get the JSON data from the request body
    product_data = request.get_json()

    # Extract the features the model pipeline was trained on
    sample = {
        'Product_Weight': product_data['Product_Weight'],
        'Product_Sugar_Content': product_data['Product_Sugar_Content'],
        'Product_Allocated_Area': product_data['Product_Allocated_Area'],
        'Product_Type': product_data['Product_Type'],
        'Product_MRP': product_data['Product_MRP'],
        'Store_Establishment_Year': product_data['Store_Establishment_Year'],
        'Store_Size': product_data['Store_Size'],
        'Store_Location_City_Type': product_data['Store_Location_City_Type'],
        'Store_Type': product_data['Store_Type'],
    }

    # Convert the extracted data into a Pandas DataFrame
    input_data = pd.DataFrame([sample])

    # Make the prediction
    predicted_sales = model.predict(input_data)[0]

    # Convert predicted_sales to a Python float (rounded), since NumPy float32
    # values raise a datatype error when passed directly to jsonify
    predicted_sales = round(float(predicted_sales), 2)

    return jsonify({'Predicted Sales (in dollars)': predicted_sales})

# Define an endpoint for batch prediction (POST request)
@superkart_sales_predictor_api.post('/v1/superkartbatch')
def predict_sales_batch():
    """
    This function handles POST requests to the '/v1/superkartbatch' endpoint.
    It expects a CSV file containing product/store details for multiple rows,
    keyed by a Product_Id column, and returns the predicted sales totals as a
    dictionary in the JSON response.
    """
    # Get the uploaded CSV file from the request
    file = request.files['file']

    # Read the CSV file into a Pandas DataFrame
    input_data = pd.read_csv(file)

    # Product_Id is only used to key the response, not as a model feature
    product_ids = input_data['Product_Id'].tolist()
    input_data = input_data.drop(columns=['Product_Id'])

    # Make predictions for every row in the DataFrame
    predicted_sales = model.predict(input_data).tolist()
    predicted_sales = [round(float(sale), 2) for sale in predicted_sales]

    # Create a dictionary of predictions with product IDs as keys
    output_dict = dict(zip(product_ids, predicted_sales))

    return output_dict

# Run the Flask application in debug mode if this script is executed directly
if __name__ == '__main__':
    superkart_sales_predictor_api.run(debug=True)
