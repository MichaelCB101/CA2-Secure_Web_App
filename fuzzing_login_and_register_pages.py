import requests
import socket
import time

#add the url and later we will point it to the pages that have forms
HOME_URL = "http://127.0.0.1:5000"
#add a payload that will be used as fuzzing  payload including SQLi, XSS, binary fuzz, etc.. for input validation
#it includes empty strings, long string, xss and sqli payloads, path traversal attempts
FUZZING_PAYLOAD = [
    "",
    "A" * 5000,
    "<script>alert('Hello');</script>",
    "' OR 1=1 --",
    "\x00\x01\"",
    "DROP TABLE users",
    "DROP TABLE players",
    "<script>alert('1');</script>",
    "../../../etc/passwd",
    "cd ..",
    "ls",
    "pwd",
    "/bin/sh",
    "a" * 500
]

#this is a payload sending malformed network packets  to the site, through tcp socket, this will test the network and site resilience
#it sends old and malformed http versions, path traversal, binary string, corrupted headers, bad requests to break the site
MALF_NET_PACKETS = [
    b"GET / HTTP/0.9\r\n",
    b"GET / HTTP/1.1\r\n",
    b"BADREQUEST /!! HTTP/1.1\r\nHost: localhost\r\n\r\n",
    b"GET /../../../etc/passwd HTTP/1.1\r\nHost: localhost\r\n\r\n",
    b"POST / login HTTP/1.1\r\nHost: \r\n",
    b"\x00\xff\xaa\x00\r\n"
]

#this function will send the input validation fuzzing payload to the web forms at each endpoint that has a form.
def fuzzing_login_and_register(endpoint):
    url = f"{HOME_URL}{endpoint}"
    print(f"----- FUzzing {url}----")

#this code takes the endpoints from the web app and loads in each field from the forms in a list
    if endpoint == "/login":
        fields = {"username","password"}
    elif endpoint == "/register":
        fields = {"username","email","nickname","password"}
    elif endpoint == "/players":
        fields = {"name","team","position","ppg","biography", "contract"}
    elif endpoint == "/schedule":
        fields = {"date","opponent","venue","notes"}
    else:
        print("Invalid endpoint")
        return

#this code loops through all the payloads and will then build a request body for each field in all the forms for each of the endpoints
    #listed above and will insert the payload in the fields
    for payload in FUZZING_PAYLOAD:
        pload_data = {field: payload for field in fields}

    #this code will send a post request with a JSON bosy as the payload data
        try:
            res = requests.post(url, json=pload_data)
            status_code = res.status_code
            #prints the first 20 letters of payload and the status code after payload execution
            print(f"Payload: {repr(payload[:20])} -> status: {status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending in payload {payload}: {e}")


#this function does the same as the above but it takes the malformed network packet payload instead
#and it sends it through a tcp socket connection to the server, which bypasses flask routes
#it tests robustenss and resistence to network attacks
def net_fuzz():
    print("-------- Fuzzing the network with malformed requests --------")

    for packet in MALF_NET_PACKETS:
        print(f"----- Fuzzing {packet}----")

    #this creates a tcp socket connection and it connects to the flask server running the app, and sends the malfomed packets
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(("127.0.0.1", 5000))
            s.send(packet)
    #this code captures the response from each data input sent and prints it to the console
            try:
                response = s.recv(2048)
                print("response:", response)
            except socket.timeout:
                print("timeout")
            s.close()
            #we include a delay for each packet here also to not overload the server
            time.sleep(1)
        except socket.error as e:
            print(f"Error sending in packet {packet}: {e}")

if __name__ == "__main__":
    fuzzing_login_and_register("/login")
    fuzzing_login_and_register("/register")
    fuzzing_login_and_register("/players")
    fuzzing_login_and_register("/schedule")
    net_fuzz()