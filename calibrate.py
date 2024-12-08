#!/usr/bin/python3
import time
import sys
import gpiod
from hx711 import HX711

try:
    # Initialize gpiod chip
    print("Initializing GPIO...")
    chip = gpiod.Chip("0", gpiod.Chip.OPEN_BY_NUMBER)
    
    # Initialize HX711
    print("Initializing HX711...")
    hx = HX711(dout=38, pd_sck=40, gain=128, chip=chip)
    
    # Reset and tare
    print("\nResetting scale...")
    hx.reset()
    time.sleep(0.5)
    
    print("\nTaring...")
    offset = hx.tare(15)  # Use 15 readings for better accuracy
    print("Tare complete")
    
    print("\nPut a known weight on the scale...")
    input("Press Enter when ready")
    
    # Get weight reading
    val = hx.get_weight(5)  # Average of 5 readings
    print(f"\nRaw value: {val}")
    weight = input("Enter exact weight in grams: ")
    
    try:
        weight_value = float(weight)
        # Calculate reference unit
        reference_unit = val / weight_value
        print(f"\nReference unit: {reference_unit}")
        print("Save this reference unit for your main program")
        
        # Set the reference unit
        hx.set_reference_unit(reference_unit)
        
        print("\nTesting scale with new reference unit...")
        print("Add or remove weights to test")
        print("Press CTRL+C to exit\n")
        
        while True:
            val = hx.get_weight(5)  # Average of 5 readings
            print(f"Weight: {val:.1f}g")
            hx.power_down()
            hx.power_up()
            time.sleep(0.5)
            
    except ValueError:
        print("Invalid weight entered!")
        sys.exit(1)

except (KeyboardInterrupt, SystemExit):
    print("\nCleaning up...")
    sys.exit()
