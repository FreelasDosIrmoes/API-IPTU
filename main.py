# from app import app_flask

# if __name__ == "__main__":
#     app_flask.run(debug=True)

from rpa.rpa import Automation

robot = Automation()
robot.process_flux_current_year('48517852','JORGE')