import os
import random
import PySimpleGUI as simG


def generate_workload(num_processes, max_arrival_time, max_cpu_bursts, min_io_burst, max_io_burst, min_cpu_burst,
                      max_cpu_burst):
    workload = []
    for i in range(num_processes):
        process_id = i
        arrival_time = random.randint(0, max_arrival_time)
        cpu_bursts = []
        num_cpu_bursts = random.randint(1, max_cpu_bursts)
        for j in range(num_cpu_bursts):
            cpu_burst_duration = random.randint(min_cpu_burst, max_cpu_burst)
            io_burst_duration = random.randint(min_io_burst, max_io_burst)
            cpu_bursts.append(cpu_burst_duration)
            cpu_bursts.append(io_burst_duration)
        cpu_bursts.pop()  # Remove last IO burst
        workload.append([process_id, arrival_time] + cpu_bursts)
    return workload


simG.theme('LightGrey1')

layout = [
    [simG.Text('Workload Generator')],
    [simG.Text('Number of processes:'), simG.InputText(size=(10, 1))],
    [simG.Text('Max arrival time:'), simG.InputText(size=(10, 1))],
    [simG.Text('Max number of CPU bursts:'), simG.InputText(size=(10, 1))],
    [simG.Text('Min IO burst duration:'), simG.InputText(size=(10, 1))],
    [simG.Text('Max IO burst duration:'), simG.InputText(size=(10, 1))],
    [simG.Text('Min CPU burst duration:'), simG.InputText(size=(10, 1))],
    [simG.Text('Max CPU burst duration:'), simG.InputText(size=(10, 1))],
    [simG.Text('Save directory:'), simG.InputText(key='save_dir'), simG.FolderBrowse()],
    [simG.Button('Generate workload'), simG.Cancel()]
]

window = simG.Window('Workload Generator', layout)

while True:
    event, values = window.read()
    if event in (None, 'Cancel'):
        break
    elif event == 'Generate workload':
        try:
            num_processes = int(values[0])
            max_arrival_time = int(values[1])
            max_cpu_bursts = int(values[2])
            min_io_burst = int(values[3])
            max_io_burst = int(values[4])
            min_cpu_burst = int(values[5])
            max_cpu_burst = int(values[6])
            save_dir = values['save_dir']
            if not os.path.exists(save_dir):
                raise Exception('Invalid save directory')
            workload = generate_workload(num_processes, max_arrival_time, max_cpu_bursts, min_io_burst, max_io_burst,
                                         min_cpu_burst, max_cpu_burst)
            filename = os.path.join(save_dir, 'workload.txt')
            with open(filename, 'w') as f:
                for process in workload:
                    f.write(','.join(str(x) for x in process) + '\n')
            simG.popup('Workload generated successfully!', title='Success')
        except Exception as e:
            simG.popup(str(e), title='Error')

window.close()
