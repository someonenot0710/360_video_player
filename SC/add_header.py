from os import listdir
from os.path import isfile, join

mypath="./"

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

for line in onlyfiles:
    if "m4s" in line:
        with open(line, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            line1 = "X-Original-Url: https://www.example.org/"+line
            line2 = "HTTP/1.1 200 OK"
            f.write(line1.rstrip('\r\n')+'\n'+line2.rstrip('\r\n')+'\n'+'\n'+content)
    #       f.write(line.rstrip('\r\n') + '\n' + content)
    #       print(line)
