import requests


def check_internet():
    url = "http://www.google.com"
    timeout = 5
    try:
        requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False


def main():
    # Usage
    if check_internet():
        print("Internet is available")
    else:
        print("Internet is not available")


if __name__ == "__main__":
    main()
