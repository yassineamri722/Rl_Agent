# shared_state.py
import threading

latest_action_data = None
data_lock = threading.Lock()
