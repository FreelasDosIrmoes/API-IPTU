from app import app_flask

if __name__ == "__main__":
    app_flask.run(debug=False, port=5001, host="0.0.0.0")

