import re
import sys

file = sys.argv[1]

pat = r'time (.*?), type \d \((.*?)\), code \((.*?)\)'
time_pat = r'time (.*?),'
event_pat = r'type \d \((.*?)\)'
code_pat = r'code \d \((.*?)\)'

with open(file, 'r') as fin:
    with open(file+".csv", 'w+') as out:
        i=0
        for line in fin:
            time = re.search(time_pat, line)
            event = re.search(event_pat, line)
            code = re.search(code_pat, line)
            try:
                time = time[1]
                i+=1
            except:
                time = ""
            try:
                event = event[1]
            except:
                event = ""
            try:
                code = code[1]
            except:
                code = ""
            print(time, event, code)
            if time=="":
                pass
            elif (event=="" and code==""):
                out.write(str(i)+","+time+","+"SYN_REPORT"+"\n")
            else:
                out.write(str(i)+","+time+","+event+","+code+"\n")
                