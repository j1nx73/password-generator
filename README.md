# Password Manager - Flask Web Interface

A secure, modern web-based password manager built with Flask that provides a beautiful visual interface for generating, storing, and managing passwords.

## Features

### 🔐 Password Generation
- **Single Password Generation**: Create secure passwords with customizable options
- **Multiple Password Generation**: Generate multiple passwords at once
- **Customizable Options**:
  - Password length (4-50 characters)
  - Character types (uppercase, lowercase, numbers, symbols)
  - Exclude ambiguous characters (0, O, l, 1)
- **Real-time Strength Analysis**: See password strength as you generate

### 💾 Password Management
- **Secure Storage**: Passwords stored locally in CSV format
- **User Authentication**: Secure login system with master password
- **Password Vault**: View, search, and manage all saved passwords
- **Export Functionality**: Export passwords to CSV files
- **Search Capabilities**: Find passwords by website or email

### 🔒 Security Features
- **Password Strength Checker**: Analyze existing passwords for security
- **Master Password Protection**: All data protected by user's master password
- **Local Storage**: No cloud storage - your data stays on your device
- **Secure Hashing**: Passwords hashed using Werkzeug security

### 🎨 Modern Web Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Bootstrap 5**: Modern, clean UI components
- **Font Awesome Icons**: Beautiful iconography throughout
- **Interactive Elements**: Copy buttons, password visibility toggles
- **Real-time Feedback**: Visual feedback for all actions

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd PasswordGenerator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the web interface**
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - Create an account or login with existing credentials

## Usage

### First Time Setup
1. Visit `http://localhost:5000`
2. Click "Register" to create a new account
3. Choose a strong master password (minimum 8 characters)
4. Login with your credentials

### Generating Passwords
1. Navigate to "Generate Password" from the dashboard
2. Adjust settings:
   - Set password length using the slider
   - Select character types to include
   - Choose whether to exclude ambiguous characters
3. Click "Generate Password"
4. Copy the generated password or save it directly

### Saving Passwords
1. Go to "Save Password" from the dashboard
2. Fill in the required fields:
   - Website/Service name
   - Email or username
   - Password (or generate one)
3. Add optional notes
4. Click "Save Password"

### Managing Passwords
1. View all passwords in "View Passwords"
2. Search for specific passwords using "Search Passwords"
3. Export your password vault using the export function
4. Edit or delete passwords as needed

## File Structure

```
PasswordGenerator/
├── app.py                 # Main Flask application
├── main.py               # Core password generator and manager logic
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── templates/           # HTML templates
│   ├── base.html       # Base template with navigation
│   ├── login.html      # Login page
│   ├── register.html   # Registration page
│   ├── dashboard.html  # Main dashboard
│   ├── generate.html   # Password generation page
│   ├── generate_multiple.html  # Multiple password generation
│   ├── check_strength.html    # Password strength checker
│   ├── save_password.html     # Save password form
│   ├── view_passwords.html    # Password vault view
│   └── search_passwords.html  # Search functionality
├── static/              # Static files
│   ├── css/
│   │   └── style.css    # Custom CSS styles
│   └── js/
│       └── script.js    # JavaScript utilities
├── passwords.csv        # Password storage (created automatically)
└── users.csv           # User accounts (created automatically)
```

## Security Considerations

### Data Storage
- All passwords are stored locally in CSV files
- No data is transmitted to external servers
- Master passwords are securely hashed using Werkzeug
- CSV files should be kept secure and backed up regularly

### Password Security
- Generated passwords use cryptographically secure random generation
- Password strength analysis provides detailed feedback
- Support for excluding ambiguous characters
- Minimum password length requirements

### Web Security
- Session-based authentication
- CSRF protection through Flask
- Secure password hashing
- Input validation and sanitization

## Customization

### Styling
- Modify `static/css/style.css` to customize the appearance
- The application uses Bootstrap 5 for responsive design
- Font Awesome icons can be replaced or customized

### Functionality
- Add new password generation options in `main.py`
- Extend the password strength checker with additional criteria
- Implement additional export formats
- Add password categories or tags

### Security Enhancements
- Implement two-factor authentication
- Add password expiration dates
- Create password sharing functionality
- Add audit logging

## Troubleshooting

### Common Issues

**Port already in use**
```bash
# Change the port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Permission errors with CSV files**
- Ensure the application has write permissions in the directory
- Check that CSV files are not open in other applications

**Import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- JavaScript must be enabled
- Local storage access required

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section
2. Review the code comments
3. Create an issue in the repository

## Changelog

### Version 1.0.0
- Initial release with Flask web interface
- Password generation and management
- User authentication system
- Modern responsive design
- Export functionality
- Search capabilities 
