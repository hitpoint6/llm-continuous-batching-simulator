import asyncio
import random
import string
import curses

# Function to generate a random word
def generate_word():
    length = random.randint(3, 10)
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Function to process a request
async def process_request(request_id, screen, request_status):
    words = []
    for _ in range(30):
        word = generate_word()
        words.append(word)
        request_status[request_id] = f"Request {request_id}: " + ' '.join(words)
        update_display(screen, request_status)
        await asyncio.sleep(0.1)  # 100ms delay

# Worker / Consumer coroutine to handle requests
async def worker(screen, request_status):
    while True:
        request_id = await request_queue.get()
        if request_id is None:
            break
        await process_request(request_id, screen, request_status)
        # Queue.task_done() decreases the internal counter of unfinished tasks.
        request_queue.task_done()

# Function to update the display
def update_display(screen, request_status):
    screen.clear()
    screen.addstr("Enter 'r' to add a new request or 'q' to quit:\n")
    for request_id, status in request_status.items():
        screen.addstr(f"{status}\n")
    screen.refresh()

# Function to add a request to the queue
async def add_request(request_id, screen, request_status):
    try:
        await request_queue.put(request_id)
    except asyncio.QueueFull:
        request_status[request_id] = f"Queue is full. Request {request_id} cannot be added."
        update_display(screen, request_status)

# Function to handle user input
async def handle_input(screen):
    while True:
        user_input = await asyncio.to_thread(screen.getstr)
        yield user_input.decode('utf-8')

# Main function to run the curses application
async def main(screen):
    global request_queue
    request_queue = asyncio.Queue(maxsize=10)

    request_status = {}

    # Create and start worker coroutines, consumer
    num_worker_threads = 3
    workers = [asyncio.create_task(worker(screen, request_status)) for _ in range(num_worker_threads)]

    update_display(screen, request_status)


    # Simulate incoming requests, producer
    request_id_counter = 1
    async for user_input in handle_input(screen):
        if user_input == 'r':
            await add_request(request_id_counter, screen, request_status)
            request_id_counter += 1
        elif user_input == 'q':
            break

    # Stop worker coroutines
    for _ in range(num_worker_threads):
        # Add None to the queue to stop the Consumer while True loop
        await request_queue.put(None)
    await asyncio.gather(*workers)

    screen.addstr("All requests processed.\n")
    screen.refresh()
    screen.getch()

curses.wrapper(lambda screen: asyncio.run(main(screen)))
