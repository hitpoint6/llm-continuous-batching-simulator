import queue
import threading
import time
import random
import string
import curses

# Function to generate a random word
def generate_word():
    length = random.randint(3, 10)
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Function to process a request
def process_request(request_id, screen, request_status):
    words = []
    for _ in range(30):
        word = generate_word()
        words.append(word)
        request_status[request_id] = f"Request {request_id}: " + ' '.join(words)
        update_display(screen, request_status)
        time.sleep(0.1)  # 100ms delay

# Worker thread to handle requests
def worker(screen, request_status):
    while True:
        request_id = request_queue.get()
        if request_id is None:
            break
        process_request(request_id, screen, request_status)
        request_queue.task_done()

# Function to update the display
def update_display(screen, request_status):
    screen.clear()
    screen.addstr("Enter 'r' to add a new request or 'q' to quit:\n")
    for request_id, status in request_status.items():
        screen.addstr(f"{status}\n")
    screen.refresh()

# Function to add a request to the queue
def add_request(request_id, screen, request_status):
    try:
        request_queue.put_nowait(request_id)
        # request_status[request_id] = f"Request {request_id} added to the queue."
        # update_display(screen, request_status)
    except queue.Full:
        request_status[request_id] = f"Queue is full. Request {request_id} cannot be added."
        update_display(screen, request_status)

# Main function to run the curses application
def main(screen):
    global request_queue
    request_queue = queue.Queue(maxsize=10)

    request_status = {}

    # Create and start worker threads
    num_worker_threads = 3
    threads = []
    for i in range(num_worker_threads):
        t = threading.Thread(target=worker, args=(screen, request_status))
        t.start()
        threads.append(t)

    # Simulate incoming requests
    request_id_counter = 1
    while True:
        update_display(screen, request_status)
        user_input = screen.getstr().decode('utf-8')
        if user_input == 'r':
            add_request(request_id_counter, screen, request_status)
            request_id_counter += 1
        elif user_input == 'q':
            break

    # Stop worker threads
    for i in range(num_worker_threads):
        request_queue.put(None)
    for t in threads:
        t.join()

    screen.addstr("All requests processed.\n")
    screen.refresh()
    screen.getch()

curses.wrapper(main)
