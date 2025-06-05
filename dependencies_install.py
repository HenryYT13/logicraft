import os
import sys

def cls_s():
    if sys.platform.startswith('win'):
        os.system('cls')
    else:
        os.system('clear')

cls_s()
print("This file is to install the dependencies")
os.system("pip install flet[all]")
os.system("pip install pygame")
os.system("pip install asyncio")
os.system("pip install json")
os.system("pip install time")
os.system("pip install threading")
os.system("pip install subprocess")
os.system("pip install tkinter")
os.system("pip install requests")
os.system("pip install datetime")

cls_s()

print("Dependencies installed")
print("Now you can run the code")