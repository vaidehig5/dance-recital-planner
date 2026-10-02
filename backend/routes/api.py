from dataclasses import asdict

from flask import Blueprint, jsonify, request

from backend.parsers.errors import SpreadsheetError
from backend.parsers.spreadsheet_parser import parse_spreadsheet

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/health")
def health():
    return jsonify(status="ok", app="dance-recital-planner")


@api_bp.post("/upload")
def upload():
    uploaded_file = request.files.get("file")
    if uploaded_file is None or uploaded_file.filename == "":
        return jsonify(error="No file was uploaded. Please choose a .csv or .xlsx file."), 400

    try:
        columns = parse_spreadsheet(uploaded_file.filename, uploaded_file.read())
    except SpreadsheetError as error:
        return jsonify(error=str(error)), 400

    return jsonify(columns=[asdict(column) for column in columns])