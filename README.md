🧠 Multi-Threaded Web Server – OS Concepts Visualization

Developed by Team CYBER SHADOWS

This project is an interactive visualization of core Operating System concepts — Threads, Semaphores, Mutex Locks, and Scheduling Algorithms (FIFO, Round Robin, Priority) — using a custom-built multi-threaded Python web server and a dynamic web-based frontend.

The backend, written in Python (socket + threading), simulates concurrent client requests with synchronization control and resource limitation using BoundedSemaphore and Lock. The frontend, built with HTML, Tailwind CSS, and Chart.js, lets users send multiple requests, observe thread activity, and compare the performance of different scheduling techniques in real-time.

Each request logs its queue wait time, processing duration, and thread details, while the dashboard visualizes live progress, response times, and automatically highlights the best-performing scheduling algorithm.

🚀 Features:

Real-time visualization of multithreading and scheduling

Interactive dashboard with live logs and charts

OS-level concepts like concurrency, mutex, and semaphores

Performance comparison of FIFO, RR, and Priority scheduling

Automatic detection of the most efficient scheduling technique

🖥️ Tech Stack:
Python, Socket Programming, Threading, Tailwind CSS, JavaScript, Chart.js
