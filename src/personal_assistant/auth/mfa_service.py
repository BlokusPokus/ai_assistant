"""
Multi-Factor Authentication (MFA) Service for TOTP.

This service provides:
- TOTP secret generation and validation
- QR code generation for authenticator apps
- Backup codes generation and management
- Device trust management
"""

import base64
import secrets
from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Dict, List, Optional

import pyotp
import qrcode

from personal_assistant.config.settings import settings


class MFAService:
    """Service for TOTP-based Multi-Factor Authentication."""

    def __init__(self, issuer: Optional[str] = None):
        """
        Initialize MFA service.

        Args:
            issuer: Issuer name for TOTP (defaults to settings)
        """
        self.issuer = issuer or settings.MFA_TOTP_ISSUER
        self.backup_codes_count = settings.MFA_BACKUP_CODES_COUNT
        self.trusted_device_days = settings.MFA_TRUSTED_DEVICE_DAYS

    def generate_totp_secret(self, user_id: int) -> str:
        """
        Generate a secure TOTP secret for a user.

        Args:
            user_id: User identifier for secret generation

        Returns:
            Base32 encoded TOTP secret
        """
        # Generate a cryptographically secure random secret
        return pyotp.random_base32()

    def generate_qr_code(self, secret: str, user_email: str) -> str:
        """
        Generate QR code for authenticator apps.

        Args:
            secret: TOTP secret
            user_email: User's email for provisioning URI

        Returns:
            Base64 encoded PNG image data URL
        """
        # Create TOTP object
        totp = pyotp.TOTP(secret)

        # Generate provisioning URI for authenticator apps
        provisioning_uri = totp.provisioning_uri(
            name=user_email, issuer_name=self.issuer
        )

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, "PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    def verify_totp(
        self, secret: str, token: str, window: Optional[int] = None
    ) -> bool:
        """
        Verify TOTP token with configurable window.

        Args:
            secret: TOTP secret
            token: Token to verify
            window: Time window tolerance (defaults to settings)

        Returns:
            True if token is valid, False otherwise
        """
        if window is None:
            window = settings.MFA_TOTP_WINDOW

        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=window)

    def generate_backup_codes(self, count: Optional[int] = None) -> List[str]:
        """
        Generate backup codes for account recovery.

        Args:
            count: Number of backup codes to generate

        Returns:
            List of backup codes
        """
        if count is None:
            count = self.backup_codes_count

        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric codes
            # Using only uppercase letters and numbers for better readability
            code = "".join(
                secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(8)
            )
            codes.append(code)

        return codes

    def verify_backup_code(
        self, user_id: int, code: str, stored_codes: List[str]
    ) -> bool:
        """
        Verify and consume a backup code.

        Args:
            user_id: User identifier
            code: Backup code to verify
            stored_codes: List of stored backup codes

        Returns:
            True if code is valid, False otherwise

        Note:
            This method should be called within a transaction to ensure
            the consumed code is properly removed from storage.
        """
        if not stored_codes:
            return False

        # Normalize code (uppercase, remove spaces)
        normalized_code = code.upper().strip()

        if normalized_code in stored_codes:
            # Remove used code (should be done in database transaction)
            stored_codes.remove(normalized_code)
            return True

        return False

    def generate_device_hash(self, device_info: Dict[str, Any]) -> str:
        """
        Generate a hash for device identification.

        Args:
            device_info: Device information dictionary

        Returns:
            Device hash string
        """
        # Create a deterministic string from device info
        device_string = f"{device_info.get('browser', '')}-{device_info.get('os', '')}-{device_info.get('device', '')}"

        # Use a hash of the device string for consistency
        import hashlib

        hash_object = hashlib.sha256(device_string.encode())
        return hash_object.hexdigest()[:16]  # Return first 16 characters

    def is_device_trusted(
        self, device_hash: str, trusted_devices: List[Dict[str, Any]]
    ) -> bool:
        """
        Check if a device is trusted.

        Args:
            device_hash: Device hash to check
            trusted_devices: List of trusted device records

        Returns:
            True if device is trusted, False otherwise
        """
        if not trusted_devices:
            return False

        now = datetime.utcnow()

        for device in trusted_devices:
            if device.get("hash") == device_hash:
                # Check if trust hasn't expired
                trusted_until = device.get("trusted_until")
                if trusted_until:
                    trust_expires = datetime.fromisoformat(trusted_until)
                else:
                    continue
                if now < trust_expires:
                    return True

        return False

    def add_trusted_device(
        self, device_info: Dict[str, Any], trusted_devices: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Add a device to trusted devices list.

        Args:
            device_info: Device information
            trusted_devices: Current list of trusted devices

        Returns:
            Updated list of trusted devices
        """
        device_hash = self.generate_device_hash(device_info)
        trust_expires = (
            datetime.utcnow() + timedelta(days=self.trusted_device_days)
        ).isoformat()

        # Create trusted device record
        trusted_device = {
            "hash": device_hash,
            "device_info": device_info,
            "trusted_at": datetime.utcnow().isoformat(),
            "trusted_until": trust_expires,
        }

        # Check if device is already trusted
        existing_hashes = [d.get("hash") for d in trusted_devices]
        if device_hash not in existing_hashes:
            trusted_devices.append(trusted_device)

        return trusted_devices

    def remove_trusted_device(
        self, device_hash: str, trusted_devices: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove a device from trusted devices list.

        Args:
            device_hash: Device hash to remove
            trusted_devices: Current list of trusted devices

        Returns:
            Updated list of trusted devices
        """
        return [d for d in trusted_devices if d.get("hash") != device_hash]

    def cleanup_expired_trusted_devices(
        self, trusted_devices: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove expired trusted devices.

        Args:
            trusted_devices: Current list of trusted devices

        Returns:
            Updated list with expired devices removed
        """
        now = datetime.utcnow()
        active_devices = []

        for device in trusted_devices:
            trusted_until = device.get("trusted_until")
            if trusted_until:
                trust_expires = datetime.fromisoformat(trusted_until)
                if now < trust_expires:
                    active_devices.append(device)

        return active_devices
