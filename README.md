CPU Scheduling Simulator

This project is an Operating Systems simulation project developed using Python and Tkinter, the program simulates CPU scheduling algorithms and demonstrates 
how processes are managed and executed inside an operating system using a Multi-Level Feedback Queue (MLFQ) scheduling approach.

The simulator supports multiple scheduling algorithms, including Round Robin (RR), Shortest Remaining Time First (SRTF), and First Come First Serve (FCFS). 
Processes are dynamically moved between queues based on their execution behavior and CPU burst times.

The project provides a graphical user interface (GUI) that allows the user to load workload files, set scheduling parameters such as time quantums and alpha value, 
start the simulation, pause/resume execution, and monitor process execution in real time.

The simulator calculates important scheduling metrics such as:
- Waiting Time
- Finish Time
- CPU Utilization
- Process Execution Order

The workload file contains process information including:
- Process ID
- Arrival Time
- CPU Bursts
- I/O Bursts

This project demonstrates core Operating Systems concepts including:
- CPU Scheduling
- Multi-Level Feedback Queue (MLFQ)
- Process Management
- Preemptive Scheduling
- Queue Management
- CPU and I/O Burst Handling
- Process State Simulation

Technologies used:
- Python
- Tkinter
- Threading
- Queue Data Structure
