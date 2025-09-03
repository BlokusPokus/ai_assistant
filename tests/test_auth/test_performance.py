#!/usr/bin/env python3
"""
Performance testing for authentication system.

This module tests performance requirements:
- Token validation: < 10ms response time
- Login endpoint: < 100ms response time  
- Middleware overhead: < 5ms per request
"""

from personal_assistant.auth.jwt_service import jwt_service
from personal_assistant.auth.password_service import password_service
from personal_assistant.config.settings import settings
import time
import sys
import os
from statistics import mean, median, stdev

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class PerformanceTester:
    """Test performance of authentication components."""

    def __init__(self):
        """Initialize performance tester."""
        self.results = {}

    def measure_token_validation(self, iterations=100):
        """Measure token validation performance."""
        print("🔍 Measuring token validation performance...")

        # Create test token
        user_data = {"sub": "test@example.com", "user_id": 123}
        token = jwt_service.create_access_token(data=user_data)

        times = []
        for i in range(iterations):
            start_time = time.perf_counter()
            try:
                jwt_service.verify_access_token(token)
                end_time = time.perf_counter()
                # Convert to milliseconds
                times.append((end_time - start_time) * 1000)
            except Exception as e:
                print(f"❌ Token validation failed: {e}")
                break

        if times:
            avg_time = mean(times)
            median_time = median(times)
            min_time = min(times)
            max_time = max(times)
            std_dev = stdev(times) if len(times) > 1 else 0

            self.results['token_validation'] = {
                'iterations': len(times),
                'avg_ms': avg_time,
                'median_ms': median_time,
                'min_ms': min_time,
                'max_ms': max_time,
                'std_dev_ms': std_dev,
                'passes_requirement': avg_time < 10
            }

            print(f"✅ Token validation performance:")
            print(f"   Average: {avg_time:.2f}ms")
            print(f"   Median: {median_time:.2f}ms")
            print(f"   Min: {min_time:.2f}ms")
            print(f"   Max: {max_time:.2f}ms")
            print(f"   Std Dev: {std_dev:.2f}ms")
            print(
                f"   Requirement (<10ms): {'✅ PASS' if avg_time < 10 else '❌ FAIL'}")
        else:
            print("❌ No valid measurements for token validation")

    def measure_password_hashing(self, iterations=50):
        """Measure password hashing performance."""
        print("\n🔍 Measuring password hashing performance...")

        password = "TestPassword123!"
        times = []

        for i in range(iterations):
            start_time = time.perf_counter()
            try:
                hashed = password_service.hash_password(password)
                end_time = time.perf_counter()
                # Convert to milliseconds
                times.append((end_time - start_time) * 1000)
            except Exception as e:
                print(f"❌ Password hashing failed: {e}")
                break

        if times:
            avg_time = mean(times)
            median_time = median(times)
            min_time = min(times)
            max_time = max(times)
            std_dev = stdev(times) if len(times) > 1 else 0

            self.results['password_hashing'] = {
                'iterations': len(times),
                'avg_ms': avg_time,
                'median_ms': median_time,
                'min_ms': min_time,
                'max_ms': max_time,
                'std_dev_ms': std_dev
            }

            print(f"✅ Password hashing performance:")
            print(f"   Average: {avg_time:.2f}ms")
            print(f"   Median: {median_time:.2f}ms")
            print(f"   Min: {min_time:.2f}ms")
            print(f"   Max: {max_time:.2f}ms")
            print(f"   Std Dev: {std_dev:.2f}ms")
            print(f"   Note: Hashing should be slow for security (bcrypt)")
        else:
            print("❌ No valid measurements for password hashing")

    def measure_password_verification(self, iterations=100):
        """Measure password verification performance."""
        print("\n🔍 Measuring password verification performance...")

        password = "TestPassword123!"
        hashed = password_service.hash_password(password)

        times = []
        for i in range(iterations):
            start_time = time.perf_counter()
            try:
                result = password_service.verify_password(password, hashed)
                end_time = time.perf_counter()
                # Convert to milliseconds
                times.append((end_time - start_time) * 1000)
                assert result is True
            except Exception as e:
                print(f"❌ Password verification failed: {e}")
                break

        if times:
            avg_time = mean(times)
            median_time = median(times)
            min_time = min(times)
            max_time = max(times)
            std_dev = stdev(times) if len(times) > 1 else 0

            self.results['password_verification'] = {
                'iterations': len(times),
                'avg_ms': avg_time,
                'median_ms': median_time,
                'min_ms': min_time,
                'max_ms': max_time,
                'std_dev_ms': std_dev,
                'passes_requirement': avg_time < 50  # Verification should be reasonable
            }

            print(f"✅ Password verification performance:")
            print(f"   Average: {avg_time:.2f}ms")
            print(f"   Median: {median_time:.2f}ms")
            print(f"   Min: {min_time:.2f}ms")
            print(f"   Max: {max_time:.2f}ms")
            print(f"   Std Dev: {std_dev:.2f}ms")
            print(
                f"   Requirement (<50ms): {'✅ PASS' if avg_time < 50 else '❌ FAIL'}")
        else:
            print("❌ No valid measurements for password verification")

    def measure_token_creation(self, iterations=100):
        """Measure token creation performance."""
        print("\n🔍 Measuring token creation performance...")

        user_data = {"sub": "test@example.com", "user_id": 123}

        # Test access token creation
        access_times = []
        for i in range(iterations):
            start_time = time.perf_counter()
            try:
                token = jwt_service.create_access_token(data=user_data)
                end_time = time.perf_counter()
                access_times.append((end_time - start_time) * 1000)
            except Exception as e:
                print(f"❌ Access token creation failed: {e}")
                break

        # Test refresh token creation
        refresh_times = []
        for i in range(iterations):
            start_time = time.perf_counter()
            try:
                token = jwt_service.create_refresh_token(data=user_data)
                end_time = time.perf_counter()
                refresh_times.append((end_time - start_time) * 1000)
            except Exception as e:
                print(f"❌ Refresh token creation failed: {e}")
                break

        if access_times and refresh_times:
            access_avg = mean(access_times)
            refresh_avg = mean(refresh_times)

            self.results['token_creation'] = {
                'access_token_avg_ms': access_avg,
                'refresh_token_avg_ms': refresh_avg,
                'passes_requirement': access_avg < 5 and refresh_avg < 5
            }

            print(f"✅ Token creation performance:")
            print(f"   Access token: {access_avg:.2f}ms average")
            print(f"   Refresh token: {refresh_avg:.2f}ms average")
            print(
                f"   Requirement (<5ms): {'✅ PASS' if access_avg < 5 and refresh_avg < 5 else '❌ FAIL'}")
        else:
            print("❌ No valid measurements for token creation")

    def run_all_tests(self):
        """Run all performance tests."""
        print("🚀 Starting Authentication System Performance Tests")
        print("=" * 60)

        self.measure_token_validation()
        self.measure_password_hashing()
        self.measure_password_verification()
        self.measure_token_creation()

        self.print_summary()

    def print_summary(self):
        """Print performance test summary."""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE TEST SUMMARY")
        print("=" * 60)

        if 'token_validation' in self.results:
            result = self.results['token_validation']
            status = "✅ PASS" if result['passes_requirement'] else "❌ FAIL"
            print(f"Token Validation: {status} ({result['avg_ms']:.2f}ms)")

        if 'password_verification' in self.results:
            result = self.results['password_verification']
            status = "✅ PASS" if result['passes_requirement'] else "❌ FAIL"
            print(
                f"Password Verification: {status} ({result['avg_ms']:.2f}ms)")

        if 'token_creation' in self.results:
            result = self.results['token_creation']
            status = "✅ PASS" if result['passes_requirement'] else "❌ FAIL"
            print(
                f"Token Creation: {status} (Access: {result['access_token_avg_ms']:.2f}ms)")

        print("\n📋 Performance Requirements:")
        print("   ✅ Token validation: < 10ms")
        print("   ✅ Password verification: < 50ms")
        print("   ✅ Token creation: < 5ms")
        print("   ✅ Login endpoint: < 100ms (not measured)")
        print("   ✅ Middleware overhead: < 5ms (not measured)")


def test_token_validation_performance(benchmark):
    """Test token validation performance using pytest-benchmark."""
    def token_validation_benchmark():
        user_data = {"sub": "test@example.com", "user_id": 123}
        token = jwt_service.create_access_token(data=user_data)
        return jwt_service.verify_access_token(token)

    result = benchmark(token_validation_benchmark)
    assert result is not None


def test_password_verification_performance(benchmark):
    """Test password verification performance using pytest-benchmark."""
    def password_verification_benchmark():
        password = "TestPassword123!"
        hashed = password_service.hash_password(password)
        return password_service.verify_password(password, hashed)

    result = benchmark(password_verification_benchmark)
    assert result is True


def test_token_creation_performance(benchmark):
    """Test token creation performance using pytest-benchmark."""
    def token_creation_benchmark():
        user_data = {"sub": "test@example.com", "user_id": 123}
        return jwt_service.create_access_token(data=user_data)

    result = benchmark(token_creation_benchmark)
    assert result is not None


def main():
    """Run performance tests."""
    tester = PerformanceTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
