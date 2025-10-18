# 🌱 Green Growth - GROOT

A comprehensive smart plant monitoring system designed to optimize plant growth through real-time environmental monitoring and automated control.

## 📋 Project Overview

Green Growth - GROOT is a complete solution for plant enthusiasts and gardeners who want to monitor and control their plants' growing environment. The system tracks temperature, humidity, light intensity, and manages water pumps to ensure optimal plant health.

## 🏗️ Project Structure

```
GreenGrowth_GROOT/
├─ Doc/                    # Documentation
├─ EmbeddedSolution/       # Hardware/embedded components
├─ WebUI/                  # Web dashboard application
│  └─ firebase-flask-app/  # Flask web application
└─ README.md              # This file
```

## 🚀 Features

- **Real-time Monitoring**: Track temperature, humidity, and light levels
- **Smart Irrigation**: Automated water pump control
- **Web Dashboard**: Interactive charts and controls
- **Mobile Responsive**: Access from any device
- **Historical Data**: View trends and patterns over time

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: Firebase Firestore
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Chart.js
- **Hardware**: Embedded sensors and actuators

## 🚀 Quick Start

1. **Navigate to WebUI**
```bash
cd WebUI/firebase-flask-app
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Run Application**
```bash
python run.py
```

4. **Access Dashboard**
Open: http://127.0.0.1:5000

## 📊 Components

### WebUI
Interactive web dashboard with real-time sensor monitoring, historical charts, and pump control.

### EmbeddedSolution
Hardware components including sensors, pumps, and microcontrollers for data collection and control.

### Documentation
Project documentation and setup guides.

## 🌱 Plant Monitoring

The system monitors key environmental factors:
- **Temperature**: Optimal range 18-30°C
- **Humidity**: Ideal range 30-70%
- **Light**: Appropriate intensity 200-1000 lux
- **Watering**: Smart pump control based on plant needs

## 📱 Access

- **Web Dashboard**: http://127.0.0.1:5000
- **Mobile Friendly**: Responsive design for all devices
- **Real-time Updates**: Live data refresh every 30 seconds

## 🔧 Configuration

The system runs in test mode by default. For production use, configure Firebase credentials in the `.env` file.

## 📄 License

© 2024 Green Growth - GROOT. All rights reserved.

---

**Grow Smart, Grow Green! 🌱**