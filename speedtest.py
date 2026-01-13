import speedtest
#pip install speedtest-cli

def check_internet_speed():
    st = speedtest.speedtest()

    print("..... Testing Speed .....")

    download = st.download() / 1_000_000
    upload = st.download() / 1_000_000

    st.get_best_server()
    ping = st.results.ping

    return {
        'download' : round(download, 2),
        'upload' : round(upload, 2),
        'ping': round(ping, 2)

    }

while True:
    try:
        speed = check_internet_speed()
        
        print(f"Download: {speed['download']} Mbps")
        print(f"Upload: {speed['upload']} Mbps")
        print(f"Ping: {speed['ping']} Mbps")
        break

    except TypeError:
        print("Module not found..... Perhaps you didn't install the module prehand... \n Try: pip install speedtest-cli")