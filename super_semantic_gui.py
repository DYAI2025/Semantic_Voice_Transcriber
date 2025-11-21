"""
DEPRECATED: Use svt_core.ui.semantic_gui instead.

This file provides backward compatibility for existing scripts.
Will be removed in version 2.0.
"""

import warnings
import sys

warnings.warn(
    "super_semantic_gui.py is deprecated. "
    "Import from 'svt_core.ui.semantic_gui' instead, "
    "or use the main SVT GUI: python3 svt.py",
    DeprecationWarning,
    stacklevel=2
)

# Redirect to new location
from svt_core.ui.semantic_gui import *

if __name__ == "__main__":
    print("\n⚠️  WARNING: This entry point is deprecated!")
    print("   Please use: python3 svt.py")
    print("   Or import from: svt_core.ui.semantic_gui\n")

    # Run the GUI anyway for compatibility
    from svt_core.ui.semantic_gui import main
    main()
