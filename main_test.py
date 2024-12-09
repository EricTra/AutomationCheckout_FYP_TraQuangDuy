#!/usr/bin/python3
import cv2
import os
import sys
import time
import signal
import gpiod
from edge_impulse_linux.image import ImageImpulseRunner
from hx711 import HX711

# Constants
REFERENCE_UNIT = 186.0897222218  # Replace with your calibrated reference unit
runner = None

# Tracking variables
list_label = []
list_weight = []
count = 0

def now():
    return round(time.time() * 1000)

def get_weight(hx, num_readings=20):
    """Measure weight using HX711."""
    try:
        val = hx.get_weight(num_readings)
        return round(val, 1)
    except Exception as e:
        print(f"Error reading weight: {e}")
        return 0

def init_hx711():
    """Initialize the HX711 load cell."""
    print("Initializing scale...")
    chip = gpiod.Chip("0", gpiod.Chip.OPEN_BY_NUMBER)
    hx = HX711(dout=38, pd_sck=40, gain=128, chip=chip)
    hx.reset()
    hx.set_reference_unit(REFERENCE_UNIT)
    print("Scale initialized successfully")
    return hx

def process_detection(label, weight):
    """Process and display detection results."""
    global count, list_label, list_weight
    print(f"\nProcessing detection: {label} with weight {weight}g")
   
    if weight > 2:  # Filter noise for weights below 2g
        list_weight.append(weight)
        list_label.append(label)
        count += 1
        print(f"Detection Count: {count}")
       
        if count > 1 and list_label[-1] != list_label[-2]:
            print("New item detected!")
            print(f"Previous item: {list_label[-2]}")
            print(f"Current item: {list_label[-1]}")
            print(f"Weight: {weight}g")
    time.sleep(0.5)

def sigint_handler(sig, frame):
    """Handle program interruption (Ctrl+C)."""
    print("\nInterrupted by user")
    if runner:
        runner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def main():
    """Main function to load the model, process camera frames, and detect objects."""
    try:
        print("\n=== Initializing System ===")
        hx = init_hx711()

        print("\n=== Loading Model ===")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        modelfile = os.path.join(dir_path, "automationcheckout_fyp-linux-aarch64-v4.eim")
        print(f"Loading model from: {modelfile}")

        if not os.path.exists(modelfile):
            print(f"Error: Model file not found at {modelfile}")
            return

        with ImageImpulseRunner(modelfile) as runner:
            try:
                print("\n=== Initializing Model ===")
                model_info = runner.init()
                print(f"Model loaded: {model_info['project']['owner']} / {model_info['project']['name']}")
                labels = model_info['model_parameters']['labels']
                print(f"Available labels: {labels}")

                print("\n=== Starting Detection Loop ===")
                print("Press Ctrl+C to exit")

                frame_count = 0
                for res, img in runner.classifier(0):  # Use camera port 0
                    frame_count += 1
                    print(f"\rProcessing frame {frame_count}", end='')  # Increment frame count
                   
                    # Debug: Print full response
                    print("\nFull response from classifier:", res)

                    if "classification" in res["result"].keys():
                        predictions = res["result"]["classification"]
                        print("\nPredictions found:")
                       
                        # Print all scores
                        for label, score in predictions.items():
                            print(f"  {label}: {score:.2f}")

                        # Focus on 'Apple' with a lower confidence threshold
                        if "Apple" in predictions:
                            score = predictions["Apple"]
                            print(f"Apple confidence score: {score:.2f}")
                            if score > 0.3:  # Reduced confidence threshold
                                print(f"\nApple detected with confidence: {score:.2f}")
                                weight = get_weight(hx)
                                print(f"Weight: {weight} grams")
                                process_detection("Apple", weight)

                    time.sleep(0.1)  # Small delay to reduce CPU usage

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
