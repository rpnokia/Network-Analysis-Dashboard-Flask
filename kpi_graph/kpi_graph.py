import os
import pandas as pd
from openpyxl import load_workbook
import numpy as np
from datetime import datetime
import zipfile
from flask import Flask, render_template, request, send_file, Blueprint

app = Flask(__name__)
kpi_graph = Blueprint('kpi_graph', __name__, template_folder='templates')

@kpi_graph.route('/kpi_graph')
def home():
    return render_template('kpigraph_index.html')

input_folder = os.path.join(os.path.dirname(__file__),  "kpigraph_input")

@kpi_graph.route('/upload_graph', methods=['GET', 'POST'])
def upload():
    global uploaded_data, uploaded_filename
    if 'file' in request.files:
        file = request.files['file']
        if file:
            uploaded_filename = file.filename
            file.save(os.path.join(input_folder, uploaded_filename))
            uploaded_data = pd.read_excel(os.path.join(input_folder, uploaded_filename))
    return render_template('kpigraph_upload.html')

@kpi_graph.route('/generate_graph', methods=['GET','POST'])
def generate_graph():
    # Read Excel file
    df = uploaded_data.copy()

    # Get unique values for the filter dropdowns
    unique_dates = df['Date'].unique()
    unique_kpi_names = df['Kpi_Name'].unique()
    unique_msc_names = df['MSC_Name'].unique()

    if request.method == 'POST':
        # Get selected filters from the form
        selected_date = request.form['date_filter']
        selected_kpi_name = request.form['kpi_filter']
        selected_msc_name = request.form['msc_filter']

        # Filter DataFrame based on the selected filters
        selected_data = df[(df['Date'] == selected_date) &
                           (df['Kpi_Name'] == selected_kpi_name) &
                           (df['MSC_Name'] == selected_msc_name)][['Hour', 'Final']]
    else:
        # Default to the first values if no filters are selected
        selected_data = df[(df['Date'] == unique_dates[0]) &
                           (df['Kpi_Name'] == unique_kpi_names[0]) &
                           (df['MSC_Name'] == unique_msc_names[0])][['Hour', 'Final']]

    # Convert DataFrame to JSON for JavaScript
    data_json = selected_data.to_json(orient='records')

    return render_template('kpigraph_generate.html',
                           data_json=data_json,
                           unique_dates=unique_dates,
                           unique_kpi_names=unique_kpi_names,
                           unique_msc_names=unique_msc_names)