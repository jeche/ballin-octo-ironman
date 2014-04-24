
#!/bin/bash

# This script opens 4 terminal windows.

i="0"

while [ $i -lt 500 ]
do
python grabRage.py
i=$[$i+1]
sleep 9
done