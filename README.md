# DATA-MANAGMANT-FOR-OPTICAL-SHOP
# Shivam Opticals

A lightweight Python desktop application for managing customer data at an optical shop. This application allows you to store customer information, prescriptions, frame and lens details, and costs.

## Features

- Add, update, and search customer records
- Store prescription data for both eyes (SPH, CYL, AXE, ADD)
- Track frame and lens information
- Calculate and store cost details
- Modern, user-friendly interface
- Database storage for reliable data persistence
- Cross-platform (Windows, Mac, Linux)

## Installation

### Pre-built Executable (Windows)

1. Download the `ShivamOpticals.exe` file from the releases section
2. Double-click the executable to run the application
3. No installation required - it's a portable application

### Building from Source

#### Requirements
- Python 3.6 or higher
- Tkinter (usually included with Python)
- SQLite (included with Python)

#### Windows
1. Clone or download this repository
2. Double-click the `build_exe.bat` file
3. The executable will be created in the `dist` folder

#### Mac/Linux
1. Clone or download this repository
2. Install required packages: `pip install pyinstaller pillow`
3. Run the build script: `python build.py`
4. The executable will be created in the `dist` folder

## How to Use

1. **Launch the Application**: 
   - Double-click the executable file

2. **Add a New Customer**:
   - Fill in the customer details (name, phone, prescription, etc.)
   - Enter frame and lens information
   - Enter costs (frame cost and lens cost will automatically calculate the total)
   - Click "Save Customer"

3. **Search for Customers**:
   - Use the search box in the "Customer List" tab to find customers by name, phone, or frame
   - Click the "Search Customers" button to see results

4. **View or Edit Customer Details**:
   - Double-click on any customer in the list to view all details
   - To edit a customer, you'll need to re-enter their information in the Add Customer tab
   
5. **Clear the Form**:
   - Click "Clear Form" to reset all fields

## Data Storage

All data is stored in a SQLite database file (`optical_shop.db`) in the same directory as the application. This means:
- Data persists between application runs
- You can back up your data by copying this file
- No internet connection required - works completely offline

## Development

To run the application in development mode:
```
python main.py
```

## License

This software is provided as-is, with no warranties expressed or implied.

---

Developed for Shivam Optical | 2025
