import socket
import threading
import time
import sys
import json
import random

# --- Configuration ---
HOST = '0.0.0.0'
PORT = 8081
MAX_CONNECTIONS = 5
MAX_CONCURRENT_WORKERS = 3

# --- OS Concepts: Shared Resources ---
REQUEST_COUNT = 0
COUNTER_LOCK = threading.Lock()
MAX_WORKERS_SEMAPHORE = threading.BoundedSemaphore(MAX_CONCURRENT_WORKERS)

# --- Scheduling Mode (default FIFO) ---
SCHEDULING_MODE = "FIFO"  # Can be "FIFO", "RR", "PRIORITY"

def simulate_scheduling_behavior():
    """Simulate scheduling impact using artificial delays."""
    global SCHEDULING_MODE
    if SCHEDULING_MODE == "RR":
        # Round Robin → break work into small bursts
        for _ in range(3):
            time.sleep(1)
    elif SCHEDULING_MODE == "PRIORITY":
        # Priority-based → random delay to simulate faster high-priority tasks
        time.sleep(random.uniform(1.0, 2.0))
    else:
        # FIFO → single continuous block
        time.sleep(3)

def handle_client(conn, addr):
    thread_name = threading.current_thread().name

    print(f"[{thread_name}] Waiting for worker slot (Semaphore Acquire)...")
    start_queue_wait = time.time()
    MAX_WORKERS_SEMAPHORE.acquire()
    queue_wait_time = time.time() - start_queue_wait
    print(f"[OS] Thread {thread_name} acquired slot for {addr[0]}:{addr[1]} after waiting {queue_wait_time:.2f}s")

    current_request_number = -1
    start_processing = time.time()

    try:
        COUNTER_LOCK.acquire()
        global REQUEST_COUNT
        REQUEST_COUNT += 1
        current_request_number = REQUEST_COUNT
        COUNTER_LOCK.release()

        request_data = conn.recv(1024).decode('utf-8')
        if not request_data:
            return

        first_line = request_data.split('\n')[0].strip()
        print(f"[{thread_name}] (Req #{current_request_number}) Request: {first_line}")

        # Simulated CPU Scheduling / Work
        simulate_scheduling_behavior()

        processing_time = time.time() - start_processing
        total_time = queue_wait_time + processing_time

        response_data = {
            "status": "success",
            "request_number": current_request_number,
            "thread_name": thread_name,
            "queue_wait_time": round(queue_wait_time, 2),
            "processing_time": round(processing_time, 2),
            "total_time": round(total_time, 2),
            "scheduling_mode": SCHEDULING_MODE,
            "message": f"Processed successfully using {SCHEDULING_MODE} scheduling."
        }

        json_body = json.dumps(response_data)
        http_response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            f"Content-Length: {len(json_body)}\r\n"
            "\r\n"
            f"{json_body}"
        )

        conn.sendall(http_response.encode('utf-8'))

    except Exception as e:
        print(f"[{thread_name}] Error: {e}")
    finally:
        conn.close()
        MAX_WORKERS_SEMAPHORE.release()
        print(f"[OS] Thread {thread_name} finished and released slot.")

def main():
    global SCHEDULING_MODE

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(MAX_CONNECTIONS)

        print(f"[INIT] Server running on port {PORT}")
        print("----------------------------------------------------------------")
        print(f"Semaphore limit: {MAX_CONCURRENT_WORKERS} threads")
        print(f"Backend API URL: http://127.0.0.1:{PORT}/")
        print("----------------------------------------------------------------")

        while True:
            conn, addr = server_socket.accept()

            # Peek first line to detect scheduling mode updates
            initial_data = conn.recv(1024, socket.MSG_PEEK).decode("utf-8")
            if "/setmode" in initial_data:
                try:
                    mode = initial_data.split("mode=")[1].split()[0].strip().upper()
                    if mode in ["FIFO", "RR", "PRIORITY"]:
                        SCHEDULING_MODE = mode
                        print(f"[MAIN] Scheduling mode updated → {SCHEDULING_MODE}")

                    response_data = {"status": "mode_changed", "scheduling_mode": SCHEDULING_MODE}
                    json_body = json.dumps(response_data)
                    conn.sendall((
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: application/json\r\n"
                        "Access-Control-Allow-Origin: *\r\n"
                        f"Content-Length: {len(json_body)}\r\n"
                        "\r\n"
                        f"{json_body}"
                    ).encode("utf-8"))
                    conn.close()
                    continue
                except:
                    pass

            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr,),
                name=f"Worker-{threading.active_count()}"
            )
            client_thread.daemon = True
            client_thread.start()

    except KeyboardInterrupt:
        print("\n[MAIN] Server shutting down...")
    finally:
        server_socket.close()
        print("[MAIN] Server socket closed.")

if __name__ == "__main__":
    main()
