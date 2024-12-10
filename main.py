#!/usr/bin/python3
import cv2
import os
import sys
import time
import signal
import gpiod
import requests
from edge_impulse_linux.image import ImageImpulseRunner
from hx711 import HX711

# Constants
REFERENCE_UNIT = 186.0897222218
SERVER_URL = "https://vpaygo.onrender.com/api/detections"
runner = None

# Global variables
count = 0
list_label = []
list_weight = []

# Product pricing
PRODUCT_PRICES = {
    'Apple': {'base_price': 10, 'rate': 0.01},
    'Monaco': {'base_price': 15, 'rate': 0},
    'Lays': {'base_price': 20, 'rate': 0}
}

def calculate_price(label, weight):
    if label in PRODUCT_PRICES:
        price_info = PRODUCT_PRICES[label]
        return price_info['base_price'] + (weight * price_info['rate'])
    return 0

def get_weight(hx, num_readings=20):
    try:
        val = hx.get_weight(num_readings)
        return round(val, 1)
    except Exception as e:
        print(f"Error reading weight: {e}")
        return 0

def init_hx711():
    print("Initializing scale...")
    chip = gpiod.Chip("0", gpiod.Chip.OPEN_BY_NUMBER)
    hx = HX711(dout=38, pd_sck=40, gain=128, chip=chip)
    hx.reset()
    print("Taring scale...")
    hx.set_reference_unit(REFERENCE_UNIT)
    hx.tare()
    print("Scale initialized successfully")
    return hx

def process_detection(label, weight):
    global count, list_label, list_weight
    print(f"\nProcessing detection: {label} with weight {weight}g")
   
    if weight > 2:
        try:
            # Calculate price and send to server
            price = calculate_price(label, weight)
            data = {
                "product": label,
                "weight": weight,
                "price": price
            }
            
            # Add retry mechanism
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        SERVER_URL, 
                        json=data,
                        headers={'Content-Type': 'application/json'},
                        timeout=5  # Add timeout
                    )
                    
                    if response.status_code == 200:
                        print(f"Sent to server successfully: {label}, {weight}g, ${price}")
                        break
                    else:
                        print(f"Server returned status code: {response.status_code}")
                        if attempt < max_retries - 1:
                            print(f"Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                except requests.exceptions.RequestException as e:
                    print(f"Request failed: {e}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)

            list_weight.append(weight)
            list_label.append(label)
            count += 1
            print(f"Detection Count: {count}")
            
            if count > 1 and list_label[-1] != list_label[-2]:
                print("New item detected!")
                print(f"Previous item: {list_label[-2]}")
                print(f"Current item: {list_label[-1]}")
                print(f"Weight: {weight}g")
        except Exception as e:
            print(f"Error communicating with server: {e}")
            
    time.sleep(0.5)

def sigint_handler(sig, frame):
    print("\nInterrupted by user")
    if runner:
        runner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def main():
    try:
        print("\n=== Initializing System ===")
        hx = init_hx711()

        print("\n=== Loading Model ===")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        modelfile = os.path.join(dir_path, "autobill_fyp-linux-aarch64-v6.eim")
        print(f"Loading model from: {modelfile}")

        if not os.path.exists(modelfile):
            print(f"Error: Model file not found at {modelfile}")
            return

        with ImageImpulseRunner(modelfile) as runner:
            try:
                print("\n=== Initializing Model ===")
                model_info = runner.init()
                print(f"Model loaded: {model_info['project']['name']}")
                labels = model_info['model_parameters']['labels']
                print(f"Available labels: {labels}")

                print("\n=== Starting Detection Loop ===")
                print("Press Ctrl+C to exit")

                frame_count = 0
                last_detection = {'label': None, 'time': 0}
               
                for res, img in runner.classifier(0):
                    frame_count += 1
                    print(f"\rProcessing frame {frame_count}", end='')

                    if "result" in res and "bounding_boxes" in res["result"]:
                        boxes = res["result"]["bounding_boxes"]
                        for box in boxes:
                            if box["value"] > 0.7:
                                label = box["label"]
                                confidence = box["value"]
                                current_time = time.time()
                               
                                if (label != last_detection['label'] and
                                    current_time - last_detection['time'] > 3):
                                   
                                    print(f"\nDetected {label} with confidence {confidence:.2f}")
                                   
                                    weight = get_weight(hx)
                                    if weight > 2:
                                        print(f"Weight: {weight}g")
                                        process_detection(label, weight)
                                       
                                        last_detection = {
                                            'label': label,
                                            'time': current_time
                                        }
                                    else:
                                        print("No object detected on scale")
                   
                    time.sleep(0.1)

            except Exception as e:
                print(f"\nError during detection: {e}")
            finally:
                if runner:
                    runner.stop()
                    print("\nRunner stopped")

    except Exception as e:
        print(f"\nGlobal error: {e}")

if __name__ == "__main__":
    main()
