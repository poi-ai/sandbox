
def main():
    change()
    check()

def change():
    global TEST
    TEST = 'i'

def check():
    print(TEST)

if __name__ == '__main__':
    TEST = 'a'
    main()