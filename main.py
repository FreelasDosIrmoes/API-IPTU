import threading

from app import app_flask
from app.service import schedule_process, trigger_process

if __name__ == "__main__":
    threading.Thread(target=schedule_process, args=(app_flask,)).start()
    app_flask.run(debug=True)
