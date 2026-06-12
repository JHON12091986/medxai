import time
import sys
import os

def beep():
    print('\a', end='', flush=True)

def main():
    print("Alert Beep System Active...")
    
    # Beep every 5 seconds for 30 seconds
    for _ in range(6):
        beep()
        time.sleep(5)
        
    # Beep every 30 seconds for 5 minutes
    for _ in range(10):
        beep()
        time.sleep(30)
        
    # Beep every 1 minute indefinitely
    while True:
        beep()
        time.sleep(60)

if __name__ == "__main__":
    main()
