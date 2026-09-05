"""
app.py
-------
The Flask backend. Ties together the frontend, the calculator engine,
the AI natural-language parser, and the SQLite database.

Routes:
    GET    /                       -> serves the frontend page
    POST   /api/calculate          -> evaluate a plain math expression
    POST   /api/calculate/natural  -> evaluate a natural-language question
    GET    /api/history            -> get recent calculation history
    DELETE /api/history            -> clear history
    GET    /api/stats              -> basic usage analytics
"""

from flask import Flask, render_template, request, jsonify

import calculator_engine as calc
import ai_parser
import database as db

app = Flask(__name__)
db.init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json(force=True, silent=True) or {}
    expression = data.get("expression", "")
    try:
        result = calc.evaluate(expression)
        db.save_calculation(expression, str(result), source="standard")
        return jsonify({"success": True, "expression": expression, "result": result})
    except calc.CalculatorError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


@app.route("/api/calculate/natural", methods=["POST"])
def calculate_natural():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "")
    try:
        expression = ai_parser.parse(query)
        result = calc.evaluate(expression)
        db.save_calculation(expression, str(result), source="natural_language")
        return jsonify(
            {
                "success": True,
                "query": query,
                "parsed_expression": expression,
                "result": result,
            }
        )
    except (calc.CalculatorError, ValueError) as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


@app.route("/api/history", methods=["GET"])
def history():
    limit = request.args.get("limit", 20, type=int)
    return jsonify(db.get_history(limit))


@app.route("/api/history", methods=["DELETE"])
def delete_history():
    db.clear_history()
    return jsonify({"success": True})


@app.route("/api/stats", methods=["GET"])
def stats():
    return jsonify(db.get_stats())


if __name__ == "__main__":
    # debug=True is handy for local development; turn it off in production
    app.run(debug=True, host="0.0.0.0", port=5000)
