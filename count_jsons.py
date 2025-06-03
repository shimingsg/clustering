
import glob
def collect_files(directory, pattern):
    search_path = f"{directory}/{pattern}"
    files = glob.glob(search_path, recursive=True)
    return files
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python collect.py <directory> <pattern>")
        sys.exit(1)
    directory = sys.argv[1]
    collected_files = collect_files(f"{directory}", "**/*.json")
    print(f"Collected {len(collected_files)} files")