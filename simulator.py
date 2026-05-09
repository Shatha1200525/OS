from time import sleep
from tkinter.filedialog import askopenfilename
from tkinter import *
import threading
from queue import Queue


class Process:
    def __init__(self, processID, arrivalTime, CPUBurstsList, IOBurstsList):
        self.processID = processID
        self.arrivalTime = arrivalTime
        self.CPUBurstsList = CPUBurstsList
        self.IOBurstsList = IOBurstsList
        self.SumOfCPUBurst = sum(CPUBurstsList)
        self.RemOfCPU = self.SumOfCPUBurst
        self.startTime = -1
        self.waitCheck = False
        self.initialCPUBurstSum = sum(CPUBurstsList)
        self.nextPredictDuration = 0
        self.whatQueue = 1
        self.doneCPUBurst = []
        self.finishTime = 0
        self.timesPreempted = 0


queue_rr1 = Queue()
queue_rr2 = Queue()
queue_srtf = Queue()
queue_fcfs = Queue()

realTime = 0
input_file = None
sleepTime = 0.3
processing = []
doneProcesses = []
paused = False
runCheck = False
waitQueue = []
CPU_not_used_time = 0
RunningProcess = None
fcfsPreemptCheck = None


def fileRead(file_path):
    with open(file_path, "r") as f:
        processes = []
        for i in f:
            temp = i.split(',')
            temp[-1] = temp[-1].rstrip()
            temp = [int(x) for x in temp]
            processes.append(temp)
        return processes


def askUserForFile():
    global input_file
    input_file = askopenfilename()
    fileLabel.config(text=input_file)


def buttonSimulationFunc():
    if runCheck:
        return
    processes = fileRead(input_file)
    global realTime
    realTime = 0
    startMLFQ(processes)


def waitTime():
    while paused:
        sleep(sleepTime)
    else:
        sleep(sleepTime)


def pauseButtonFunc():
    global paused
    if runCheck:
        if paused:
            pauseButton.config(text="Pause")
            paused = False
        else:
            pauseButton.config(text="Continue")
            paused = True


def startMLFQ(ps):
    global queue_rr1, queue_rr2, queue_srtf, queue_fcfs
    global runCheck
    runCheck = True

    timeQuantum1 = int(q1_entry.get())
    timeQuantum2 = int(q2_entry.get())
    alpha = float(alpha_entry.get())
    processes = []

    for tempProcess in ps:
        processID = tempProcess[0]
        arrivalTime = tempProcess[1]
        CPUBurstsList = []
        IOBurstsList = []
        for i in range(2, len(tempProcess)):
            if i % 2 == 0:
                CPUBurstsList.append(tempProcess[i])
            else:
                IOBurstsList.append(tempProcess[i])
        processes.append(Process(processID, arrivalTime, CPUBurstsList, IOBurstsList))
        processes[-1].nextPredictDuration = (alpha * processes[-1].CPUBurstsList[0])

    multiLevelFeedBackQueue(processes, timeQuantum1, timeQuantum2, alpha)
    info = ""
    process = 0
    while process < len(processing) - 1:
        temp = processing[process][0]
        info += f'| {processing[process][1]}'

        while process < len(processing) - 1:
            if temp == processing[process][0]:
                process += 1
            else:
                break
        info += f' | P{temp} '
        if temp == -1:
            info += f' | nothing '
    info += f'| {processing[process][1]} |'
    print(info)
    displayInfo()
    runCheck = False


def estimateAlpha(queue, alpha):
    tempQueue = Queue()
    while not queue.empty():
        tempProcess = queue.get()
        tempProcess.nextPredictDuration = (alpha * tempProcess.CPUBurstsList[0]) + (
                tempProcess.nextPredictDuration * (1 - alpha))
        tempQueue.put(tempProcess)
    return tempQueue


def alphaSort(process_queue):
    processes = list(process_queue.queue)
    temp1 = sorted(processes, key=lambda tempProcess: tempProcess.nextPredictDuration)
    temp2 = Queue()
    for process in temp1:
        temp2.put(process)
    return temp2


def displayInfo():
    sumTemp = 0
    infoBox.delete("1.0", END)
    info = 'Processes:\n'
    for i in doneProcesses:
        tempWait = i.finishTime - i.arrivalTime - i.initialCPUBurstSum
        info += f'\nP{i.processID}:\n' \
                f'start time = {i.startTime}\n' \
                f'finish time = {i.finishTime}\n' \
                f'arrival time =  {i.arrivalTime}\n'
        sumTemp += tempWait
    sumTemp /= len(doneProcesses)
    info += f'\nwait time average for all processes: {sumTemp}\n'
    utilization = ((realTime - CPU_not_used_time) / realTime) * 100
    info += f'\ncpu utilization: {utilization}%'
    infoBox.insert(END, info)
    infoBox.update()


def multiLevelFeedBackQueue(processes, quantum1, quantum2, alpha):
    global CPU_not_used_time
    global realTime

    while waitQueue or processes or not queue_rr1.empty() or not queue_rr2.empty() or not queue_rr2.empty() or not queue_fcfs.empty():
        for tempProcess in processes:
            if tempProcess.arrivalTime <= realTime:
                queue_rr1.put(tempProcess)
                processes.remove(tempProcess)

        if not queue_rr1.empty():
            RR(processes, queue_rr1, quantum1)
        elif not queue_rr2.empty():
            RR(processes, queue_rr2, quantum2)
        elif not queue_srtf.empty():
            SRTF(alpha)
        elif not queue_fcfs.empty():
            FCFS(processes)
        else:
            if waitQueue:
                index = 0
                while index < len(waitQueue):
                    waitTime()
                    waitQueue[index].IOBurstsList[0] -= 1
                    if waitQueue[index].IOBurstsList[0] == 0:
                        waitQueue[index].IOBurstsList.remove(0)
                        waitQueue[index].waitCheck = False
                        putBackInQueue(waitQueue[index])
                        waitQueue.remove(waitQueue[index])
                        index -= 1
                    index += 1
            else:
                CPU_not_used_time += 1
                realTime += 1


def putBackInQueue(process):
    if process.whatQueue == 1:
        queue_rr1.put(process)
    elif process.whatQueue == 2:
        queue_rr2.put(process)
    elif process.whatQueue == 3:
        queue_srtf.put(process)
    elif process.whatQueue == 4:
        queue_fcfs.put(process)


def FCFS(processes):
    global CPU_not_used_time
    global realTime
    global RunningProcess
    RunningProcess = queue_fcfs.get()
    displayProcess(waitQueue)
    processing.append([RunningProcess.processID, realTime])
    if RunningProcess.startTime == -1:
        RunningProcess.startTime = realTime
    while RunningProcess.CPUBurstsList[0] > 0:
        for tempProcess in processes:
            if tempProcess.arrivalTime <= realTime:
                queue_rr1.put(tempProcess)
                processes.remove(tempProcess)
        if not queue_rr1.empty() or not queue_rr2.empty() or not queue_srtf.empty() or not queue_fcfs.empty():
            return
        waitTime()
        RunningProcess.CPUBurstsList[0] -= 1
        RunningProcess.RemOfCPU -= 1
        realTime += 1
        processing.append([RunningProcess.processID, realTime])
        index = 0
        while index < len(waitQueue):
            waitTime()
            waitQueue[index].IOBurstsList[0] -= 1
            if waitQueue[index].IOBurstsList[0] == 0:
                waitQueue[index].IOBurstsList.remove(0)
                waitQueue[index].waitCheck = False
                putBackInQueue(waitQueue[index])
                waitQueue.remove(waitQueue[index])
                index -= 1
            index += 1

    CPUFinished(RunningProcess)


def SRTF(alpha):
    global realTime
    global CPU_not_used_time
    global RunningProcess
    global fcfsPreemptCheck
    global queue_srtf
    queue_srtf = estimateAlpha(queue_srtf, alpha)
    queue_srtf = alphaSort(queue_srtf)
    RunningProcess = queue_srtf.get()
    displayProcess(waitQueue)
    if fcfsPreemptCheck is not None and fcfsPreemptCheck != RunningProcess:
        fcfsPreemptCheck.timesPreempted += 1
    fcfsPreemptCheck = RunningProcess
    if RunningProcess.timesPreempted >= 3:
        RunningProcess.SumOfCPUBurst = RunningProcess.RemOfCPU
        RunningProcess.whatQueue += 1
        putBackInQueue(RunningProcess)
        return
    if RunningProcess.startTime == -1:
        RunningProcess.startTime = realTime
    displayProcess(waitQueue)
    waitTime()
    RunningProcess.CPUBurstsList[0] -= 1
    RunningProcess.RemOfCPU -= 1
    realTime += 1
    processing.append([RunningProcess.processID, realTime])

    index = 0
    while index < len(waitQueue):
        waitTime()
        waitQueue[index].IOBurstsList[0] -= 1
        if waitQueue[index].IOBurstsList[0] == 0:
            waitQueue[index].IOBurstsList.remove(0)
            waitQueue[index].waitCheck = False
            putBackInQueue(waitQueue[index])
            waitQueue.remove(waitQueue[index])
            index -= 1
        index += 1
    if RunningProcess.CPUBurstsList[0] == 0:
        RunningProcess = CPUFinished(RunningProcess)

    if not RunningProcess.waitCheck and RunningProcess.finishTime == 0:
        putBackInQueue(RunningProcess)


def RR(processes, queue, quantum):
    global CPU_not_used_time
    global realTime

    global RunningProcess

    RunningProcess = queue.get()
    if (RunningProcess.SumOfCPUBurst - RunningProcess.RemOfCPU) >= quantum * 10:
        RunningProcess.SumOfCPUBurst = RunningProcess.RemOfCPU
        RunningProcess.whatQueue += 1
        putBackInQueue(RunningProcess)
        return
    processing.append([RunningProcess.processID, realTime])
    if RunningProcess.startTime == -1:
        RunningProcess.startTime = realTime

    for _ in range(quantum):
        displayProcess(waitQueue)
        waitTime()
        RunningProcess.CPUBurstsList[0] -= 1
        RunningProcess.RemOfCPU -= 1
        realTime += 1
        processing.append([RunningProcess.processID, realTime])
        index = 0
        while index < len(waitQueue):
            waitTime()
            waitQueue[index].IOBurstsList[0] -= 1
            if waitQueue[index].IOBurstsList[0] == 0:
                waitQueue[index].IOBurstsList.remove(0)
                waitQueue[index].waitCheck = False
                putBackInQueue(waitQueue[index])
                waitQueue.remove(waitQueue[index])
                index -= 1
            index += 1

        for tempProcess in processes:
            if tempProcess.arrivalTime <= realTime:
                queue_rr1.put(tempProcess)
                processes.remove(tempProcess)
        if RunningProcess.CPUBurstsList[0] == 0:
            RunningProcess = CPUFinished(RunningProcess)
            break
    if not RunningProcess.waitCheck and RunningProcess.finishTime == 0:
        putBackInQueue(RunningProcess)


def CPUFinished(process):
    process.doneCPUBurst.append(process.CPUBurstsList.pop(0))
    if len(process.CPUBurstsList) == 0:
        process.finishTime = realTime
        doneProcesses.append(process)
    else:
        waitQueue.append(process)
        process.waitCheck = True
    return process


def processesQueue(queue):
    info = ''
    for i in queue.queue:
        info += f'\nprocess: {i.processID}:\n' \
                f'\nRemaining CPU bursts: {i.CPUBurstsList}\n'
    return info


def displayProcess(wait_queue):
    info = ''
    info += f'time = {realTime}\n\n'
    info += 'queue number 1\n'
    info += processesQueue(queue_rr1)
    info += '====================================\n'
    info += '\nqueue number 2\n'
    info += processesQueue(queue_rr2)
    info += '====================================\n'
    info += '\nqueue number 3\n'
    info += processesQueue(queue_srtf)
    info += '====================================\n'
    info += '\nqueue number 4\n'
    info += processesQueue(queue_fcfs)
    info += '\n====================================\n'

    info += f'\nwait queue:'
    for i in wait_queue:
        info += f'\nP{i.processID}\n'
        info += '\n====================================\n'

    infoBox.delete("1.0", END)
    infoBox.insert(END, info)
    infoBox.update()


def back():
    if not runCheck:
        root.destroy()


root = Tk()

root.title("My GUI")
root.configure(bg="#ffffff")

frame = Frame(root)
frame.pack(pady=20)

backButton = Button(frame, text="Back", command=back, relief="flat", font=("Helvetica", 10))
backButton.grid(row=0, column=0, padx=10, pady=10)

q1_label = Label(frame, text='Q1', font=("Helvetica", 10))
q1_label.grid(row=1, column=0, padx=10, pady=10)

q1_entry = Entry(frame, highlightthickness=0, font=("Helvetica", 10))
q1_entry.grid(row=1, column=1, padx=10, pady=10)

q2_label = Label(frame, text='Q2', font=("Helvetica", 10))
q2_label.grid(row=2, column=0, padx=10, pady=10)

q2_entry = Entry(frame, highlightthickness=0, font=("Helvetica", 10))
q2_entry.grid(row=2, column=1)

alpha_label = Label(frame, text='Alpha', font=("Helvetica", 10))
alpha_label.grid(row=3, column=0, padx=10, pady=10)

alpha_entry = Entry(frame, highlightthickness=0, font=("Helvetica", 10))
alpha_entry.grid(row=3, column=1, padx=10, pady=10)

simulationButton = Button(frame, text='Simulate',
                          command=lambda: threading.Thread(target=buttonSimulationFunc).start(),
                          relief="flat",
                          font=("Helvetica", 10))
simulationButton.grid(row=5, column=0, padx=10, pady=10)

chooseButton = Button(frame, text='Choose File', command=askUserForFile, relief="flat", font=("Helvetica", 10))
chooseButton.grid(row=4, column=0, padx=10, pady=10)

pauseButton = Button(frame, text="Pause", relief="flat", command=pauseButtonFunc, font=("Helvetica", 10))
pauseButton.grid(row=5, column=1, padx=10, pady=10)

fileLabel = Label(frame, highlightthickness=0)
fileLabel.grid(row=4, column=1, padx=10, pady=10)

infoBox = Text(frame, width=50, height=15, font=("Helvetica", 10))
infoBox.grid(row=6, column=0, padx=10, pady=10, columnspan=2)

root.resizable(False, False)
root.mainloop()
