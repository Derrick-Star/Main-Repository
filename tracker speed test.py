# --------- Import Libraries ---------
import phonenumbers  
from phonenumbers import geocoder, carrier, timezone  
import platform  
import speedtest  

# --------- Phone Number Location ---------
number = input("Enter phone number with country code (e.g. +2349********0): ")  
try:  
    phone_number = phonenumbers.parse(number)
    
    # Getting the country and location info
    location = geocoder.description_for_number(phone_number, "en")
    country = geocoder.description_for_number(phone_number, "en")
    service_provider = carrier.name_for_number(phone_number, "en")
    time_zones = timezone.time_zones_for_number(phone_number)
    
    print(f"\n--- Phone Number Info ---")
    print(f"Phone Number: {number}")
    print(f"Country: {country}")
    print(f"Carrier: {service_provider}")
    print(f"Time Zones: {', '.join(time_zones)}")
    
    if location:
        print(f"Location: {location}")
    else:
        print("Could not retrieve location.")
        
except Exception as e:  
    print(f"Error parsing number: {e}")

# --------- System Information ---------
print("\n--- System Information ---")  
print("System:", platform.system())  
print("Node Name:", platform.node())  
print("Release:", platform.release())  
print("Version:", platform.version())  
print("Machine:", platform.machine())  
print("Processor:", platform.processor())  

# --------- Internet Speed Test ---------
print("\n--- Internet Speed Test ---")  
try:  
    st = speedtest.Speedtest()  
    download = st.download() / 1_000_000  # Convert to Mbps  
    upload = st.upload() / 1_000_000      # Convert to Mbps  
    print(f"Download speed: {download:.2f} Mbps")  
    print(f"Upload speed: {upload:.2f} Mbps")  
except Exception as e:  
    print(f"Speed test failed: {e}")