import multiprocessing
import threading

from app import app_flask
from app.service import schedule_process
from rpa.rpa import Automation

if __name__ == "__main__":
    threading.Thread(target=schedule_process, args=(app_flask,)).start()
    app_flask.run(debug=False, port=5001)


#
# robot = Automation()
# robot.process_flux_previous_years('123456789', '')
