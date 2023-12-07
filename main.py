import multiprocessing
import threading

from app import app_flask
from rpa.rpa import Automation

if __name__ == "__main__":
    app_flask.run(debug=False, port=5000)


#
# robot = Automation()
# robot.process_flux_previous_years('123456789', '')
