# VPayGo - AI-Driven Automated Checkout System

## 🌟 Project Overview
VPayGo is an AI-powered autonomous checkout system designed for retail stores and convenience stores. This system leverages advanced computer vision and real-time weight measurement to streamline the shopping experience by enabling customers to scan, weigh, and pay for items independently, reducing checkout times and improving operational efficiency.
![image](https://github.com/user-attachments/assets/b803fff9-bde3-4d5e-8668-7e0522655392)

---

## 🛠️ Technologies Used
- **Programming Language**: Python
- **Libraries and Frameworks**: OpenCV, Edge Impulse, Node.js, Express.js
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: RESTful APIs using Node.js and Express
- **Hardware**:
  - Jetson Nano Kit 2GB Developer
   ![image](https://github.com/user-attachments/assets/4d16d1e7-c9cc-4976-8f68-348c9a44d003)
  - Logitech C270 Camera  
  - Load Cell (10kg) with HX711 Module  
   ![image](https://github.com/user-attachments/assets/a683104d-437a-4e33-8c12-17a390761517)
  - And the rest of the hardware like, LCD display for jetsonano, keyboard, mouse


---

## ✨ Key Features
- **Product Detection**: Identifies items using a deep learning model trained on Edge Impulse.
- **Real-Time Weight Measurement**: Integrates with the load cell and HX711 module for accurate weight measurement.
- **Pricing Calculation**: Calculates prices based on weight and predefined product details.
- **QR Code Payment**: Generates QR codes for digital payment solutions.
- **Seamless Integration**: Combines object detection, weight measurement, and checkout functionalities in a single interface.

---

## 📥 Installation and Usage

### 1. Environment Setup
Clone the repository:
```bash
git clone https://github.com/EricTra/VPayGo.git
cd VPayGo
`````
Install the required dependencies:
```bash
pip install opencv-python requests edge-impulse-linux gpiod
`````

#### REMEMBER CONFIG JETSON NANO OPERATION & JETSON NANO WITH EDGE IMPULSE  BEFORE SET SUP ENVIROMENT: https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-2gb-devkit | https://docs.edgeimpulse.com/docs/edge-ai-hardware/gpu/nvidia-jetson

### 2. Setting Up Hardware

1. **Jetson Nano**: Connect the Logitech C270 Camera and configure GPIO pins for the load cell and HX711 module.  
   (Please follow the wiring diagram below.)

**Loadcell & HX711 Wiring:**
- **F+** (Red)
- **E-** (Black)
- **A+** (White)
- **A-** (Green)

**HX711 to Jetson Pin Mapping:**
- **GND**: Chân 6
- **DT**: Chân 38
- **SCK**: Chân 40
- **VCC**: Chân 2

2. **HX711 Calibration**:
   - Run the calibration script:
     ```bash
     python calibrate.py
     ```
   - Follow the on-screen instructions to calibrate the load cell with a known weight.
![image](https://github.com/user-attachments/assets/6178acc5-73fe-4d69-968f-ae9b9e01f132)

### 3. Running the Application
1. Train the Edge Impulse model and export it to the VPayGo directory as autobill_fyp-linux-armv7-v3.eim.
2. Start the detection system:
  ```bash
python main.py
````` 
---

## 🖼️ Demo and Screenshots
**1. System in Action:**
![image](https://github.com/user-attachments/assets/ea2f807e-8aa1-4f64-bce0-c37c2d02f105)
**Weight Measurement and Pricing**
![image](https://github.com/user-attachments/assets/45d48cde-0afd-4198-aac3-2c92ed614507)
![image](https://github.com/user-attachments/assets/e7eaa3dd-ba29-4b45-a075-e62cf1f1e4e6)
![image](https://github.com/user-attachments/assets/4b2977c9-376a-4c00-9d96-7bc75ba6762d)
## 📧 Contact Information
- Author: Trà Quang Duy
- Email: traquangduy246@gmail.com
- LinkedIn: [Trà Quang Duy](https://www.linkedin.com/in/traquangduy/)
