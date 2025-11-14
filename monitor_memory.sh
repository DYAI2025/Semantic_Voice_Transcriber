#!/bin/bash
# Memory Monitoring Script for Transcription
# Shows RAM and SWAP usage every 2 seconds

echo "=== Memory Monitoring Started ==="
echo "Press Ctrl+C to stop"
echo ""

while true; do
    clear
    echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="
    echo ""

    # Show memory usage
    free -h | head -2
    echo ""

    # Show swap usage separately
    echo "SWAP Usage:"
    free -h | grep Swap
    echo ""

    # Show Python processes memory
    echo "Python Processes (top 5 by memory):"
    ps aux | grep python | grep -v grep | sort -k4 -r | head -5 | awk '{printf "%s\t%s\t%s\n", $2, $4"%", $11}'
    echo ""

    # Warning if low memory
    FREE_MEM=$(free -m | awk 'NR==2{print $7}')
    if [ $FREE_MEM -lt 2000 ]; then
        echo "⚠️  WARNING: Only ${FREE_MEM}MB available memory!"
    fi

    # Warning if swap is high
    SWAP_USED=$(free -m | awk 'NR==3{print $3}')
    SWAP_TOTAL=$(free -m | awk 'NR==3{print $2}')
    if [ $SWAP_TOTAL -gt 0 ]; then
        SWAP_PERCENT=$((SWAP_USED * 100 / SWAP_TOTAL))
        if [ $SWAP_PERCENT -gt 80 ]; then
            echo "⚠️  WARNING: SWAP is ${SWAP_PERCENT}% full - system may freeze!"
        fi
    fi

    sleep 2
done
