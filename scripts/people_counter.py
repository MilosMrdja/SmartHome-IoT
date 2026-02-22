import time
from collections import deque
from common.mqqt_sender import batch_queue

distance_history_1 = deque(maxlen=3)
distance_history_2 = deque(maxlen=3)    


def update_distance(sensor_id, distance):
    if sensor_id == 1:
        distance_history_1.append((time.time(), distance))
    elif sensor_id == 2:
        distance_history_2.append((time.time(), distance))

def detect_direction(history):
    if len(history) < 3:
        return None

    distances = [d for _, d in history]

    if all(distances[i] > distances[i+1] for i in range(len(distances)-1)):
        return "enter"

    if all(distances[i] < distances[i+1] for i in range(len(distances)-1)):
        return "exit"

    return None


def process_motion(sensor_id):
    global people_count
    if sensor_id == 1:
        direction = detect_direction(distance_history_1)
    else:
        direction = detect_direction(distance_history_2)

    # if direction == "enter":
    #     print(True)
    # elif direction == "exit":
    #     print(False)

    if direction != None:
        return direction == "enter"