import sys
from pathlib import Path

# make `import simulation` work when pytest is run from anywhere
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
