from pathlib import Path


def main():
    filename = 'my_file.txt'
    path = Path(__file__)
    print('absolute path: ', path.resolve())
    path_to_txt = path.parent / 'my_file.txt'
    print('contents: ', path_to_txt.read_text())
    print('file name: ', path_to_txt.name)
    print('is file: ', path_to_txt.is_file())
    py_files = path_to_txt.parent.rglob("*.py")
    for file in py_files:
        print(file)


if __name__ == '__main__':
    main()
