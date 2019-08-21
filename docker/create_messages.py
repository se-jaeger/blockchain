import requests


if __name__ == "__main__":

    for i in range(50):
        response = requests.put("http://localhost:12345/add", params={"message": f"Message #{i}"})

        print(f"Message #{i} created!")