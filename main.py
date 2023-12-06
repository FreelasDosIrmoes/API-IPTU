import threading

from app import app_flask
from app.service import trigger_process, query_to_get_iptu_late

if __name__ == "__main__":
    threading.Thread(target=trigger_process, args=(app_flask,)).start()
    # app_flask.run(debug=True)
