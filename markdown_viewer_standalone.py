from markdown_viewer import start_markdown_viewer
import sys

if __name__ == "__main__":
    readme = sys.argv[1] if len(sys.argv) > 1 else "README.md"
    start_markdown_viewer(readme)