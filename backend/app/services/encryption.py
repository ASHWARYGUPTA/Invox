"""
Encryption service for securing sensitive email credentials
Uses Fernet symmetric encryption from cryptography library
"""
import os
import json
from cryptography.fernet import Fernet
from app.core.config import settings


class EncryptionService:
    """
    Service for encrypting and decrypting sensitive data
    Uses a secret key from environment variables
    """
    
    def __init__(self):
        # Get encryption key from settings or generate one
        encryption_key = getattr(settings, 'ENCRYPTION_KEY', None)
        
        if not encryption_key:
            # Generate a new key if not provided (for development only!)
            print("⚠️ WARNING: No ENCRYPTION_KEY found. Generating a temporary one.")
            print("⚠️ For production, add ENCRYPTION_KEY to your .env file!")
            encryption_key = Fernet.generate_key().decode()
        
        # Ensure key is bytes
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
        
        self.cipher = Fernet(encryption_key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt a string
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted string (base64 encoded)
        """
        if not data:
            return None
        
        encrypted_bytes = self.cipher.encrypt(data.encode())
        return encrypted_bytes.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt a string
        
        Args:
            encrypted_data: Encrypted string (base64 encoded)
        
        Returns:
            Plain text string
        """
        if not encrypted_data:
            return None
        
        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_data.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            raise ValueError("Failed to decrypt data. Key may be incorrect.")
    
    def encrypt_json(self, data: dict) -> str:
        """
        Encrypt a dictionary as JSON
        
        Args:
            data: Dictionary to encrypt
        
        Returns:
            Encrypted JSON string
        """
        json_str = json.dumps(data)
        return self.encrypt(json_str)
    
    def decrypt_json(self, encrypted_data: str) -> dict:
        """
        Decrypt JSON data back to dictionary
        
        Args:
            encrypted_data: Encrypted JSON string
        
        Returns:
            Dictionary
        """
        json_str = self.decrypt(encrypted_data)
        return json.loads(json_str)


# Global encryption service instance
encryption_service = EncryptionService()


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key
    This should be run once and the key stored in .env
    
    Returns:
        Base64 encoded encryption key
    """
    key = Fernet.generate_key()
    return key.decode()


if __name__ == "__main__":
    # Generate a new encryption key for .env file
    print("🔐 Generating new encryption key...")
    key = generate_encryption_key()
    print(f"\n✅ Add this to your .env file:")
    print(f"ENCRYPTION_KEY=\"{key}\"")
    print("\n⚠️ Keep this key secret and never commit it to version control!")
