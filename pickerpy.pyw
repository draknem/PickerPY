## This source code is licensed under WTFPL
## Project page http://shouravbr.com/PickerPY
## PickerPY version 1

from Tkinter import *
import tkFileDialog
import tkMessageBox
import ttk
import subprocess
from locale import getpreferredencoding
from datetime import datetime
import threading

root = Tk()
root.resizable(0, 0)
root.title("PickerPY v1.0")

# vars
lTab = 0  # last tab

on = False  # should script run?
a = ''  # archive path

atkType = 0

bf0 = BooleanVar()  # number
bf1 = BooleanVar()  # lowercase
bf2 = BooleanVar()  # uppercase
bfc = StringVar()  # custom input

df = ''  # dictionary path
dt = BooleanVar()  # parse type
dt.set(True)

pre = StringVar()  # prefix
suf = StringVar()  # suffix
t = IntVar()  # threads
mn = IntVar()  # minimum

tLast = 0 #time elapsed last time.
tStart = 0  # time started
tElapsed = 0  # time elapsed

nPool = '0123456789'  # list of numberical inputs
lcPool = 'abcdefghijklmnopqrstuvwxyz'  # list of lowercase inputs
ucPool = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # list of uppercase inputs
iPool = ''  # final input pool

pw = False  # pw of the archive
pTried = 0  # no of pw tried
tryPw = []  # passwords to try

# thread worker class
class tWorker(threading.Thread):
    def __init__(self, pw):
        threading.Thread.__init__(self)
        self.pw = pw+""
        #print(self.pw)
    def run(self):
        global a
        cmd = "7za t \"" + a + "\" -p\"" + self.pw + "\""
        cmd = toUnicode(cmd)
        #cmd = "7za t \"" + a + "\" -p\"" + self.pw + "\""
        #cmd = "chcp 10000 && "+ cmd
        # print cmd
        #rc = subprocess.Popen(cmd.encode('latin-1'), stdout=subprocess.PIPE, shell=True)
        cmd = prefEncode(cmd)
        rc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        self.rc = rc.wait()
# end of CLASS

# Functions
def prefEncode(s):
    return s.encode(getpreferredencoding())
def toUnicode(string):
    toReturn = '';

    for char in string:
        toReturn += unichr(ord(char));

    return toReturn

# prepare for brute force attack
def bfa():
    global iPool, nPool, ucPool, lcPool
    n = bf0.get()
    l = bf1.get()
    u = bf2.get()
    c = bfc.get()
    iPool = ""
    if(n):
        iPool += nPool
    if(l):
        iPool += lcPool
    if(u):
        iPool += ucPool
    if(c):
        iPool += c

# prepare for dictionary file attack
def dfa():
    global iPool, df
    t = dt.get()
    dictFile = open(df)
    fileLines = dictFile.readlines()
    iPool = []
    if(t == False):
        for i in range(len(fileLines)):
            iPool.append(fileLines[i].split('\n')[0])
    else:
        for i in range(len(fileLines)):
            words = fileLines[i].split('\n')[0].split(" ")
            for j in range(len(words)):
                iPool.append(words[j])
    dictFile.close()

# see if a is defined
def checkA():
    if(len(a) == 0):
        return False
    else:
        return True

# set archive path & label al
def setA():
    a0 = tkFileDialog.askopenfilename(filetypes=[('Zip Archive', '*.zip'), ('7zip Archive', '*.7z')])
    if(a0):
        global a
        a = a0
        al['text'] = a0[a0.rfind('/') + 1:]

# set dictionary file path & label dl
def setDl():
    d0 = tkFileDialog.askopenfilename(filetypes=[('Text file', '*.txt')])
    if(len(d0) > 0):
        global df
        df = d0
        dl['text'] = d0[d0.rfind('/') + 1:]

# create pw2Try
def cr8Pw2Try():
    t = ''
    for i in range(0, len(tryPw)):  # loop over for pwLen times
        t = iPool[tryPw[i]] + t
    return t

# function to fix tryPw
def fix(t):
    global pTried
    tl = len(t)
    il = len(iPool)
    for i in range(0, tl):  # loop over all the values of t
        if t[i] > (il - 1):  # check if the element is bigger than iPool's length
            t[i] = 0  # if so then change it to zero
            if i == (tl - 1):  # check if the current element is the last t's element
                t.append(0)  # if so then append another zero
                pTried = 0
            else:  # if not, increase the next element by 1
                t[i + 1] += 1
    return t

def work():
    global pw, tryPw, pTried
    tList = []
    for i in range(t.get()):  # loop & initiate the numbers of tWorkers
        pw2Try = cr8Pw2Try()
        newTWorker = tWorker(pre.get() + pw2Try + suf.get())
        newTWorker.start()
        tList.append(newTWorker)
        tryPw[0] += 1
        pTried += 1
        tryPw = fix(tryPw)
    for i in range(t.get()):
        getTWorker = tList.pop()
        getTWorker.join()  # wait for the tWorker to finish        
        if(getTWorker.rc != 2):  # return code = 2 = failed
            pw = getTWorker.pw
        else:
            pw = False
        del getTWorker
        if(pw != False):
            tList = []
            break
        else:
            return

# cycle work till the job gets done
def run():
    while((on) & (pw == False)):
        work()
        setLog()
    if(pw != False):
        stop()
        f = open(a[0:a.rfind('/') + 1] + "PickerPY.log", 'w');
        f.write("Archive: " + a[a.rfind('/') + 1:] + "\nPassword = " + pw + "\nThank you for using PickerPY.")
        f.close()
        tkMessageBox.showinfo(title="DONE!", message="Password: " + pw + ". Password saved to PickerPY.log file in the Archive's directory.")

def setLog():
    global tElapsed, tStart, tLast, tryPw, pTried
    tElapsed = (datetime.now() - tStart).total_seconds()  # get the time elapsed
    tElapsed += tLast
    
    pwl = len(tryPw)
    prob = len(iPool) ** pwl
    ll['text'] = len(tryPw)
    lt['text'] = str(pTried) + "/" + str(len(iPool) ** pwl)
    # tElapsed=(tElapsed/pTried)*((len(iPool)**pwl)-pTried)
    ts = int(tElapsed % 60)
    tm = int(tElapsed / 60)
    th = int(tm / 60)
    tm %= 60
    le['text'] = str(th) + "h " + str(tm) + "m " + str(ts) + "s"
    # le['text']=str(tElapsed)
    # print(str(pTried)+" / "+str(prob)+" = "+str(float(pTried)/prob))
    lp['value'] = round(float(pTried) / prob * 100)
    # #lp['value']=50
    root.update()

# start brute
def startB():
    if(checkA() != True):
        tkMessageBox.showinfo(title="Oops", message="Add the archive first.")
        return
    if not((len(bfc.get()) > 0) or bf1.get()or bf2.get() or bf0.get()):
        tkMessageBox.showinfo(title="Oops", message="You forgot to check or type the input fields.")
    else:
        global lTab
        lTab = 0
        for i in range(3):
            n.tab(i, state='disabled')
        n.tab(3, state='normal')
        n.select(3)
        start(0)

# start dictionary
def startD():
    if(checkA() != True):
        tkMessageBox.showinfo(title="Oops", message="Add the archive first.")
        return
    if not(len(df) > 0):
        tkMessageBox.showinfo(title="Oops", message="You forgot to add the dictionary file.")
        return
    else:
        global lTab
        lTab = 1
        for i in range(3):
            n.tab(i, state='disabled')
        n.tab(3, state='normal')
        n.select(3)
        start(1)
        
# start the script
def start(t):
    root.update()
    global on, tStart, pw, tryPw, pTried,atkType
    pw = False
    on = True
    tryPw = []
    pTried = 0
    if(t == 0):
        bfa()
    else:
        dfa()

    atkType = t
    
    for i in range(mn.get()):
        tryPw.append(0)

    btOpen.grid_forget()
    btStop.grid(column=3, row=1)

    btLoad.grid_forget()
    btSave.grid(column=3,row=3)
    
    tStart = datetime.now()
    run()
# stop the script
def stop():
    global on, lTab, tLast, tElapsed
    tLast += tElapsed
    on = False
    for i in range(3):
        n.tab(i, state='normal')
    n.select(lTab)
    n.tab(3, state='disabled')

    btSave.grid_forget()
    btLoad.grid(column=3,row=3)

#resume
def resume():
    global on, tStart
    on = True
    for i in range(3):
        n.tab(i, state="disabled")
        
    btResume.grid_forget()
    btPause.grid(column=3,row=3)
    
    tStart = datetime.now()
    run()

#bt Stop
def btStop():
    yesno = tkMessageBox.askyesno("Stop","Unsaved progress will be lost. Are you sure?")

    if(yesno):
        stop()
        btStop.grid_forget()
        btOpen.grid(column=3,row=1)
        
        btResume.grid_forget()
        btPause.grid(column=3,row=3)
    

#pause
def pause():
    global tLast, tElapsed, on
    tLast += tElapsed
    on = False
    for i in [2,3]:
        n.tab(i, state='normal') #enable only options & logs tab
    for i in [0,1]:
        n.tab(i, state="disabled")

    btPause.grid_forget()
    btResume.grid(column=3,row=3)

#load
def load():
    f = tkFileDialog.askopenfile(parent = root,
                                 title = "Load settings",
                                 initialfile = "ppsave.log",
                                 filetypes = [('Log file', '*.log')],
                                 mode = 'r')

    if(f):
        global a,atkType,tryPw,pTried,pLast,tStart
        o = f.readlines()
        for i in range(len(o)):
            o[i] = o[i].split('\n')[0]

        a = o[0]
        al['text'] = o[0][o[0].rfind('/') + 1:]
        atkType = int(o[1])

        if(atkType == 0):
            bf0.set(True if o[2][0]=="1" else False)
            bf1.set(True if o[2][1]=="1" else False)
            bf2.set(True if o[2][2]=="1" else False)

            bfc.set(o[3])
            bfa()
        else:
            df = o[2]
            dt.set(True if o[3]=="1" else False)
            dfa()

        pre.set(o[4])
        suf.set(o[5])
        t.set(o[6])
        mn.set(o[7])

        tryPw = [int(i) for i in o[8].split(',')]
        pTried = int(o[9])
        pLast = float(o[10])

        tStart = datetime.now()
        setLog()

        on = False
        for i in [2,3]:
            n.tab(i, state='normal') #enable only options & logs tab
        for i in [0,1]:
            n.tab(i, state="disabled")

        btPause.grid_forget()
        btResume.grid(column=3,row=3)

        btOpen.grid_forget()
        btStop.grid(column=3,row=1)

        btLoad.grid_forget()
        btSave.grid(column=3,row=3)
    

#save
def save():
    f = tkFileDialog.asksaveasfile(parent = root,
                                    title = "Save settings",
                                    initialfile = "ppsave.log",
                                    filetypes = [('Log file', '*.log')],
                                   mode = 'w')

    if(f):
        #global a,atkType,pwTried,tLast
        wLines = [a, atkType]

        if(atkType==0):
            c = "1" if bf0.get() else "0"
            c +=  "1" if bf1.get() else "0"
            c +=  "1" if bf2.get() else "0"

            wLines.append(c)
            wLines.append(bfc.get())
            
        else:
            wLines.append(df)
            wLines.append("1" if dt.get() else "0")

        wLines.append(pre.get());
        wLines.append(suf.get());
        wLines.append(t.get());
        wLines.append(mn.get());
        
        wLines.append(','.join(str(i) for i in tryPw))
        wLines.append(pTried)
        wLines.append(tLast)

        for i in range(len(wLines)-1):
            f.write(prefEncode(toUnicode(str(wLines[i])))+'\n')
        f.write(prefEncode(toUnicode(str(wLines[len(wLines)-1]))))
        f.close()

# GUI Markups
mainframe = ttk.Frame(root, padding=5)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
# archive select row = 1
ttk.Label(mainframe, text="Archive:").grid(column=1, row=1)
al = ttk.Label(mainframe, text="---")  # archive label
al.grid(column=2, row=1)
btOpen = ttk.Button(mainframe, text="Open", command=setA)
btOpen.grid(column=3, row=1)
btStop = ttk.Button(mainframe, text="Stop", command=btStop)
# notebook
n = ttk.Notebook(mainframe)
n.grid(column=1, row=2, columnspan=3, pady="5 0")
nt = ['Brute Force', 'Dictionary', 'Settings', 'Log']
nf = []
for i in range(4):
    nf.append(ttk.Frame(n, padding=5))
    n.add(nf[i], text=nt[i])
# 1st tab
Checkbutton(nf[0], text='numbers', variable=bf0, onvalue=True, offvalue=False).grid(column=1, row=1)
Checkbutton(nf[0], text='lowercase', variable=bf1, onvalue=True, offvalue=False).grid(column=2, row=1)
Checkbutton(nf[0], text='uppercase', variable=bf2, onvalue=True, offvalue=False).grid(column=3, row=1)
ttk.Label(nf[0], text='Custom:').grid(column=1, row=2)
ttk.Entry(nf[0], textvariable=bfc).grid(column=2, row=2, columnspan=2, sticky=(W, E))
ttk.Button(nf[0], text="Start", command=startB).grid(column=3, row=3)
# 2nd tab
ttk.Label(nf[1], text='Word file:').grid(column=1, row=1)
dl = Label(nf[1], text="---", width=15)  # word file label
dl.grid(column=2, row=1)
ttk.Button(nf[1], text="Select", command=setDl).grid(column=3, row=1)
ttk.Label(nf[1], text='Parse by').grid(column=1, row=2)
ttk.Radiobutton(nf[1], text="Word", variable=dt, value=True).grid(column=2, row=2)
ttk.Radiobutton(nf[1], text="Line", variable=dt, value=False).grid(column=3, row=2)
ttk.Button(nf[1], text="Start", command=startD).grid(column=3, row=3)
# 3rd tab
ttk.Label(nf[2], text='Prefix').grid(column=1, row=1)
ttk.Label(nf[2], text='Suffix').grid(column=2, row=1)
ttk.Label(nf[2], text='Thread').grid(column=3, row=1)
ttk.Entry(nf[2], textvariable=pre, width=12).grid(column=1, row=2)
ttk.Entry(nf[2], textvariable=suf, width=12).grid(column=2, row=2)
Spinbox(nf[2], textvariable=t, from_=1, to=5, width=3).grid(column=3, row=2)
ttk.Label(nf[2], text="Min. Length:").grid(column=1, row=3)
Spinbox(nf[2], textvariable=mn, from_=1, to=32, width=3).grid(column=2, row=3)
btLoad = ttk.Button(nf[2],text="Load", command=load)
btLoad.grid(column=3,row=3)
btSave = ttk.Button(nf[2],text="Save", command=save)
# 4th tab
ttk.Label(nf[3], text="Length", width=12).grid(column=1, row=1)
ll = ttk.Label(nf[3], text='0')  # Length
ll.grid(column=1, row=2)
ttk.Label(nf[3], text='Tried', width=12).grid(column=2, row=1)
lt = ttk.Label(nf[3], text='0/0')  # tried
lt.grid(column=2, row=2)
ttk.Label(nf[3], text="Time Elapsed", width=12).grid(column=3, row=1)
le = ttk.Label(nf[3], text="0:00:00")  # time
le.grid(column=3, row=2)
lp = ttk.Progressbar(nf[3], orient=HORIZONTAL, mode='determinate', value=20)  # progress
lp.grid(column=1, row=3, columnspan=2, padx=5, sticky=(W, E))
btPause = ttk.Button(nf[3], text="Pause", command=pause)
btPause.grid(column=3, row=3)
btResume = ttk.Button(nf[3], text="Resume", command=resume)
n.tab(3, state='disabled')
# Run GUI
root.mainloop()

