SYSTEM=$1
EXP=$2

if [[ "$SYSTEM" == "darwin" ]]; then
    echo "checking processes on darmin machine..."
    ps -axo "command"|egrep "$EXP"|grep -v grep
elif [[ "$SYSTEM" == "linux" ]]; then
    echo "checking proccess on a linux machine..."
    ps -Ao command|egrep "$EXP"|grep -v grep
fi
