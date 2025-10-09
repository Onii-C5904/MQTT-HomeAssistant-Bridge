'''
10/8/2025
Kristijan Stojanovski

Various helper functions
'''



def getFileContent(filename)->str:
    """
    Displays the content of a given file to the console.
    """
    try:
        with open(filename, 'r') as f:
            content = f.read()
            return str(content)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")