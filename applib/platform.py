"""..."""
import sys

IS_FROZEN = getattr(sys, "frozen", None) and hasattr(sys, "_MEIPASS")

IS_WIN = sys.platform.startswith("win")

IS_LINUX = sys.platform.startswith("linux")

IS_MACOS = sys.platform.startswith("darwin")