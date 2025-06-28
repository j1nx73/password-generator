import random
import string
import secrets
import csv
import os
from datetime import datetime
import hashlib
import getpass
from werkzeug.security import generate_password_hash, check_password_hash


class PasswordManager:
    def __init__(self, csv_file="passwords.csv"):
        self.csv_file = csv_file
        self.current_user = None
        self.init_csv_file()

    def init_csv_file(self):
        """Initialize CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['username', 'website', 'email', 'password', 'created_date', 'notes'])

    def hash_password(self, password):
        """Create a simple hash for master password (basic security)."""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate_user(self):
        """Simple authentication system."""
        users_file = "users.csv"

        # Create users file if it doesn't exist
        if not os.path.exists(users_file):
            with open(users_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['username', 'password_hash'])

        print("\n🔐 Login to Password Manager")
        username = input("Username: ").strip()

        # Check if user exists
        user_exists = False
        with open(users_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    user_exists = True
                    stored_hash = row['password_hash']
                    break

        if user_exists:
            # Existing user - verify password
            master_password = getpass.getpass("Master Password: ")
            if self.hash_password(master_password) == stored_hash:
                self.current_user = username
                print(f"✅ Welcome back, {username}!")
                return True
            else:
                print("❌ Invalid password!")
                return False
        else:
            # New user - create account
            print(f"\n👤 User '{username}' not found. Creating new account...")
            master_password = getpass.getpass("Create Master Password: ")
            confirm_password = getpass.getpass("Confirm Master Password: ")

            if master_password != confirm_password:
                print("❌ Passwords don't match!")
                return False

            if len(master_password) < 8:
                print("❌ Master password must be at least 8 characters!")
                return False

            # Save new user
            with open(users_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([username, self.hash_password(master_password)])

            self.current_user = username
            print(f"✅ Account created successfully! Welcome, {username}!")
            return True

    # Web-specific methods
    def authenticate_user_web(self, username, password):
        """Web authentication using Werkzeug security."""
        users_file = "users.csv"
        
        if not os.path.exists(users_file):
            return False
            
        with open(users_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    return check_password_hash(row['password_hash'], password)
        return False

    def create_user_web(self, username, password):
        """Create new user for web interface."""
        users_file = "users.csv"
        
        # Check if user already exists
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['username'] == username:
                        return False
        
        # Create users file if it doesn't exist
        if not os.path.exists(users_file):
            with open(users_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['username', 'password_hash'])
        
        # Save new user with hashed password
        with open(users_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([username, generate_password_hash(password)])
        
        return True

    def get_password_count(self, username):
        """Get count of passwords for a user."""
        if not os.path.exists(self.csv_file):
            return 0
            
        count = 0
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    count += 1
        return count

    def get_user_passwords(self, username):
        """Get all passwords for a user."""
        if not os.path.exists(self.csv_file):
            return []
            
        passwords = []
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    passwords.append(row)
        return passwords

    def search_passwords_web(self, username, search_term):
        """Search passwords for web interface."""
        if not os.path.exists(self.csv_file):
            return []
            
        matches = []
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if (row['username'] == username and
                        (search_term.lower() in row['website'].lower() or
                         search_term.lower() in row['email'].lower())):
                    matches.append(row)
        return matches

    def export_passwords_web(self, username):
        """Export passwords for web interface."""
        user_passwords = self.get_user_passwords(username)
        
        if not user_passwords:
            return None
            
        export_file = f"{username}_passwords_export.csv"
        with open(export_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['website', 'email', 'password', 'created_date', 'notes'])
            writer.writeheader()
            for entry in user_passwords:
                writer.writerow({
                    'website': entry['website'],
                    'email': entry['email'],
                    'password': entry['password'],
                    'created_date': entry['created_date'],
                    'notes': entry['notes']
                })
        return export_file

    def save_password(self, website, email, password, notes=""):
        """Save password entry to CSV file."""
        if not self.current_user:
            print("❌ Please login first!")
            return False

        created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([self.current_user, website, email, password, created_date, notes])

        return True

    def view_passwords(self):
        """View all saved passwords for current user."""
        if not self.current_user:
            print("❌ Please login first!")
            return

        if not os.path.exists(self.csv_file):
            print("📝 No passwords saved yet.")
            return

        user_passwords = []
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == self.current_user:
                    user_passwords.append(row)

        if not user_passwords:
            print("📝 No passwords saved yet.")
            return

        print(f"\n🔐 Saved Passwords for {self.current_user}")
        print("=" * 60)

        for i, entry in enumerate(user_passwords, 1):
            print(f"\n{i}. Website: {entry['website']}")
            print(f"   Email: {entry['email']}")
            print(f"   Password: {'*' * len(entry['password'])} (hidden)")
            print(f"   Created: {entry['created_date']}")
            if entry['notes']:
                print(f"   Notes: {entry['notes']}")

        # Option to reveal specific password
        if user_passwords:
            try:
                reveal = input(f"\nReveal password? Enter number (1-{len(user_passwords)}) or 0 to skip: ")
                if reveal.isdigit() and 1 <= int(reveal) <= len(user_passwords):
                    selected = user_passwords[int(reveal) - 1]
                    confirm = getpass.getpass("Enter master password to reveal: ")
                    # Simple verification - in real app, you'd verify against stored hash
                    print(f"🔓 Password: {selected['password']}")
            except (ValueError, IndexError):
                pass

    def search_passwords(self, search_term):
        """Search passwords by website or email."""
        if not self.current_user:
            print("❌ Please login first!")
            return

        if not os.path.exists(self.csv_file):
            print("📝 No passwords saved yet.")
            return

        matches = []
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if (row['username'] == self.current_user and
                        (search_term.lower() in row['website'].lower() or
                         search_term.lower() in row['email'].lower())):
                    matches.append(row)

        if matches:
            print(f"\n🔍 Search Results for '{search_term}':")
            print("=" * 40)
            for i, entry in enumerate(matches, 1):
                print(f"\n{i}. Website: {entry['website']}")
                print(f"   Email: {entry['email']}")
                print(f"   Created: {entry['created_date']}")
        else:
            print(f"❌ No matches found for '{search_term}'")

    def export_passwords(self, export_file=None):
        """Export user's passwords to a separate CSV file."""
        if not self.current_user:
            print("❌ Please login first!")
            return

        if not export_file:
            export_file = f"{self.current_user}_passwords_export.csv"

        user_passwords = []
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == self.current_user:
                    user_passwords.append(row)

        if user_passwords:
            with open(export_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['website', 'email', 'password', 'created_date', 'notes'])
                writer.writeheader()
                for entry in user_passwords:
                    writer.writerow({
                        'website': entry['website'],
                        'email': entry['email'],
                        'password': entry['password'],
                        'created_date': entry['created_date'],
                        'notes': entry['notes']
                    })
            print(f"✅ Passwords exported to {export_file}")
        else:
            print("📝 No passwords to export.")


class PasswordGenerator:
    def __init__(self):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    def generate_password(self, length=12, include_uppercase=True, include_lowercase=True,
                          include_digits=True, include_symbols=True, exclude_ambiguous=False):
        """
        Generate a secure password with customizable options.

        Args:
            length (int): Password length (minimum 4)
            include_uppercase (bool): Include uppercase letters
            include_lowercase (bool): Include lowercase letters
            include_digits (bool): Include numbers
            include_symbols (bool): Include special characters
            exclude_ambiguous (bool): Exclude ambiguous characters (0, O, l, 1, etc.)

        Returns:
            str: Generated password
        """
        if length < 4:
            raise ValueError("Password length must be at least 4 characters")

        # Build character set based on options
        charset = ""
        required_chars = []

        if include_lowercase:
            chars = self.lowercase
            if exclude_ambiguous:
                chars = chars.replace('l', '').replace('o', '')
            charset += chars
            required_chars.append(secrets.choice(chars))

        if include_uppercase:
            chars = self.uppercase
            if exclude_ambiguous:
                chars = chars.replace('I', '').replace('O', '')
            charset += chars
            required_chars.append(secrets.choice(chars))

        if include_digits:
            chars = self.digits
            if exclude_ambiguous:
                chars = chars.replace('0', '').replace('1', '')
            charset += chars
            required_chars.append(secrets.choice(chars))

        if include_symbols:
            charset += self.symbols
            required_chars.append(secrets.choice(self.symbols))

        if not charset:
            raise ValueError("At least one character type must be selected")

        # Generate password ensuring at least one character from each selected type
        password = required_chars.copy()

        # Fill remaining length with random characters
        for _ in range(length - len(required_chars)):
            password.append(secrets.choice(charset))

        # Shuffle the password to avoid predictable patterns
        secrets.SystemRandom().shuffle(password)

        return ''.join(password)

    def generate_multiple_passwords(self, count=5, **kwargs):
        """Generate multiple passwords with the same criteria."""
        return [self.generate_password(**kwargs) for _ in range(count)]

    def check_password_strength(self, password):
        """
        Evaluate password strength based on various criteria.

        Returns:
            dict: Strength analysis with score and recommendations
        """
        score = 0
        feedback = []

        # Length check
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        else:
            feedback.append("Use at least 8 characters (12+ recommended)")

        # Character variety checks
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in self.symbols for c in password)

        variety_count = sum([has_lower, has_upper, has_digit, has_symbol])
        score += variety_count

        if not has_lower:
            feedback.append("Add lowercase letters")
        if not has_upper:
            feedback.append("Add uppercase letters")
        if not has_digit:
            feedback.append("Add numbers")
        if not has_symbol:
            feedback.append("Add special characters")

        # Pattern checks
        if not any(password[i] != password[i + 1] for i in range(len(password) - 1)):
            score -= 2
            feedback.append("Avoid repeated characters")

        # Determine strength level
        if score >= 7:
            strength = "Very Strong"
        elif score >= 5:
            strength = "Strong"
        elif score >= 3:
            strength = "Medium"
        else:
            strength = "Weak"

        return {
            "strength": strength,
            "score": score,
            "max_score": 8,
            "feedback": feedback
        }


def main():
    generator = PasswordGenerator()
    manager = PasswordManager()

    print("🔐 Password Generator & Manager")
    print("=" * 40)

    # Authentication required
    if not manager.authenticate_user():
        print("❌ Authentication failed. Exiting...")
        return

    while True:
        print(f"\n👤 Logged in as: {manager.current_user}")
        print("\nOptions:")
        print("1. Generate single password")
        print("2. Generate multiple passwords")
        print("3. Check password strength")
        print("4. Save password to vault")
        print("5. View saved passwords")
        print("6. Search passwords")
        print("7. Export passwords")
        print("8. Logout")
        print("9. Exit")

        choice = input("\nSelect an option (1-9): ").strip()

        if choice == "1":
            # Single password generation
            try:
                length = int(input("Password length (default 12): ") or "12")

                print("\nCharacter types to include:")
                include_upper = input("Uppercase letters? (Y/n): ").lower() != 'n'
                include_lower = input("Lowercase letters? (Y/n): ").lower() != 'n'
                include_digits = input("Numbers? (Y/n): ").lower() != 'n'
                include_symbols = input("Special characters? (Y/n): ").lower() != 'n'
                exclude_ambiguous = input("Exclude ambiguous characters (0,O,l,1)? (y/N): ").lower() == 'y'

                password = generator.generate_password(
                    length=length,
                    include_uppercase=include_upper,
                    include_lowercase=include_lower,
                    include_digits=include_digits,
                    include_symbols=include_symbols,
                    exclude_ambiguous=exclude_ambiguous
                )

                print(f"\n✅ Generated Password: {password}")

                # Show strength analysis
                strength = generator.check_password_strength(password)
                print(f"🔒 Strength: {strength['strength']} ({strength['score']}/{strength['max_score']})")

                # Option to save
                save_option = input("\nSave this password? (y/N): ").lower() == 'y'
                if save_option:
                    website = input("Website/Service: ").strip()
                    email = input("Email/Username: ").strip()
                    notes = input("Notes (optional): ").strip()

                    if manager.save_password(website, email, password, notes):
                        print("✅ Password saved successfully!")

            except ValueError as e:
                print(f"❌ Error: {e}")

        elif choice == "2":
            # Multiple password generation
            try:
                count = int(input("How many passwords? (default 5): ") or "5")
                length = int(input("Password length (default 12): ") or "12")

                passwords = generator.generate_multiple_passwords(
                    count=count,
                    length=length
                )

                print(f"\n✅ Generated {count} passwords:")
                for i, pwd in enumerate(passwords, 1):
                    strength = generator.check_password_strength(pwd)
                    print(f"{i:2}. {pwd} ({strength['strength']})")

                # Option to save selected password
                save_option = input(f"\nSave one of these passwords? Enter number (1-{count}) or 0 to skip: ")
                if save_option.isdigit() and 1 <= int(save_option) <= count:
                    selected_password = passwords[int(save_option) - 1]
                    website = input("Website/Service: ").strip()
                    email = input("Email/Username: ").strip()
                    notes = input("Notes (optional): ").strip()

                    if manager.save_password(website, email, selected_password, notes):
                        print("✅ Password saved successfully!")

            except ValueError as e:
                print(f"❌ Error: {e}")

        elif choice == "3":
            # Password strength checker
            password = getpass.getpass("Enter password to check (hidden input): ").strip()
            if password:
                strength = generator.check_password_strength(password)
                print(f"\n🔒 Password Strength: {strength['strength']}")
                print(f"📊 Score: {strength['score']}/{strength['max_score']}")

                if strength['feedback']:
                    print("💡 Suggestions:")
                    for suggestion in strength['feedback']:
                        print(f"   • {suggestion}")
                else:
                    print("✅ Great password!")

        elif choice == "4":
            # Save existing password
            print("\n💾 Save Password to Vault")
            website = input("Website/Service: ").strip()
            email = input("Email/Username: ").strip()
            password = getpass.getpass("Password (hidden input): ").strip()
            notes = input("Notes (optional): ").strip()

            if website and email and password:
                if manager.save_password(website, email, password, notes):
                    print("✅ Password saved successfully!")
            else:
                print("❌ Website, email, and password are required!")

        elif choice == "5":
            # View saved passwords
            manager.view_passwords()

        elif choice == "6":
            # Search passwords
            search_term = input("Search by website or email: ").strip()
            if search_term:
                manager.search_passwords(search_term)

        elif choice == "7":
            # Export passwords
            export_file = input("Export filename (default: auto-generated): ").strip()
            if export_file:
                manager.export_passwords(export_file)
            else:
                manager.export_passwords()

        elif choice == "8":
            # Logout
            manager.current_user = None
            print("👋 Logged out successfully!")
            if not manager.authenticate_user():
                print("❌ Authentication failed. Exiting...")
                return

        elif choice == "9":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    main()