# Media EXIF Scanner

## Overview
Media EXIF Scanner is a Python-based desktop application designed to scan media files (images and videos) across multiple disk spaces. The application captures and stores EXIF data, including disk name, file name, file path, and hash values of the media files in a local light database.

## Features
- Select multiple disk spaces for scanning.
- Capture and store all possible EXIF data from media files.
- Compute and store hash values for images.
- User-friendly interface for easy navigation and data display.

## Project Structure
```
media-exif-scanner
├── src
│   ├── main.py               # Entry point of the application
│   ├── ui
│   │   └── app_ui.py         # UI components and layout
│   ├── scanner
│   │   └── media_scanner.py   # Logic for scanning media files
│   ├── database
│   │   └── db_manager.py      # Database management for storing media info
│   ├── utils
│   │   ├── exif_utils.py       # Utility functions for EXIF data extraction
│   │   └── hash_utils.py       # Utility functions for generating hash values
│   └── types
│       └── media_file.py       # Data structure for media files
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
└── .gitignore                  # Files and directories to ignore in version control
```

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/media-exif-scanner.git
   ```
2. Navigate to the project directory:
   ```
   cd media-exif-scanner
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```
   python src/main.py
   ```
2. Use the UI to select the disk spaces you want to scan.
3. Click the scan button to start scanning for media files.
4. View the captured EXIF data and hash values in the application interface.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.