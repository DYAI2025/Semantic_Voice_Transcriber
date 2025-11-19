#!/bin/bash
# Helper script to clear SWAP memory
# Usage: sudo ./clear_swap.sh

echo "🔍 Current SWAP status:"
free -h | grep Swap

echo ""
echo "⚠️  This will clear SWAP memory. Continue? (y/n)"
read -r response

if [ "$response" = "y" ]; then
    echo "🔄 Clearing SWAP..."
    swapoff -a && swapon -a

    if [ $? -eq 0 ]; then
        echo "✅ SWAP cleared successfully!"
        echo ""
        echo "📊 New SWAP status:"
        free -h | grep Swap
    else
        echo "❌ Failed to clear SWAP"
        exit 1
    fi
else
    echo "❌ Aborted"
    exit 0
fi
