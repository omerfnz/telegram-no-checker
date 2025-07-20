# Turkish Phone Validator

A modern Python desktop application for validating Turkish phone numbers through Telegram MTProto API. Built with MVVM architecture and CustomTkinter for a modern user interface.

## Features

- Generate random Turkish phone numbers
- Validate numbers through Telegram MTProto API
- Store results in SQLite database
- Export results in multiple formats (CSV, Excel, JSON, TXT)
- Modern dark/light theme UI
- Bulk import and processing
- Anti-robot protection with rate limiting

## Project Structure

```
turkish-phone-validator/
├── models/              # Data models and domain entities
├── services/            # External API, database, file operations
├── viewmodels/          # Business logic and UI state management
├── views/               # UI components and CustomTkinter interfaces
├── utils/               # Helper functions and utilities
├── tests/               # Unit and integration tests
├── data/                # SQLite database files (created at runtime)
├── logs/                # Application logs (created at runtime)
├── exports/             # Export files (created at runtime)
├── main.py              # Application entry point
├── config.py            # Configuration settings
└── requirements.txt     # Python dependencies
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure Telegram API credentials (see Configuration section)
4. Run the application:
   ```bash
   python main.py
   ```

## Configuration

Before using the application, you need to:

1. Get Telegram API credentials from https://my.telegram.org/
2. Set environment variables or configure through the UI:
   - `TELEGRAM_API_ID`: Your Telegram API ID
   - `TELEGRAM_API_HASH`: Your Telegram API Hash

## Development

This project follows MVVM (Model-View-ViewModel) architecture pattern:

- **Models**: Pure data classes and domain entities
- **Services**: External integrations (Telegram API, Database, File I/O)
- **ViewModels**: Business logic and state management
- **Views**: UI components and user interactions

## Requirements

- Python 3.8+
- Windows/Linux/macOS
- Telegram API credentials
- Internet connection for API calls

## License

This project is for educational purposes only. Please respect Telegram's Terms of Service and rate limits.