import time
from typing import Tuple

import numpy as np
import pytest

from next_cvat.types.mask import Mask


def create_test_mask(size: Tuple[int, int], density: float = 0.3) -> np.ndarray:
    """Create a random binary mask of given size with approximate density of True values."""
    return np.random.random(size) < density


@pytest.mark.parametrize(
    "mask_size,expected_max_time",
    [
        ((100, 100), 0.01),
        ((500, 500), 0.1),
        ((1000, 1000), 0.4),
    ],
)
def test_mask_encoding_performance(
    mask_size: Tuple[int, int], expected_max_time: float
):
    """Test that mask encoding is reasonably fast."""
    # Create a random mask
    test_mask = create_test_mask(mask_size)

    # Time the encoding operation
    start_time = time.perf_counter()
    rle = Mask.rle_encode(test_mask)
    encoding_time = time.perf_counter() - start_time

    # Also run slow version for comparison
    start_time = time.perf_counter()
    rle_slow = Mask.rle_encode_slow(test_mask)
    slow_time = time.perf_counter() - start_time

    assert rle == rle_slow, "Encoding mismatch between fast and slow versions"

    print(f"\nEncoding {mask_size} mask:")
    print(f"Fast version: {encoding_time:.4f} seconds")
    print(f"Slow version: {slow_time:.4f} seconds")
    print(f"Speedup: {slow_time/encoding_time:.1f}x")

    assert (
        encoding_time < expected_max_time
    ), f"Encoding took too long: {encoding_time:.4f} seconds"


@pytest.mark.parametrize(
    "mask_size,expected_max_time",
    [
        ((100, 100), 0.01),
        ((500, 500), 0.1),
        ((1000, 1000), 0.4),
    ],
)
def test_mask_decoding_performance(
    mask_size: Tuple[int, int], expected_max_time: float
):
    """Test that mask decoding is reasonably fast."""
    # Create a random mask and encode it
    test_mask = create_test_mask(mask_size)
    rle = Mask.rle_encode(test_mask)

    # Create a mask instance
    mask = Mask(
        label="test",
        source="test",
        occluded=0,
        z_order=0,
        rle=rle,
        top=0,
        left=0,
        height=mask_size[0],
        width=mask_size[1],
        attributes=[],
    )

    # Time both versions
    start_time = time.perf_counter()
    decoded_mask = mask.rle_decode()
    decoding_time = time.perf_counter() - start_time

    start_time = time.perf_counter()
    decoded_mask_slow = mask.rle_decode_slow()
    slow_time = time.perf_counter() - start_time

    assert np.array_equal(
        decoded_mask, decoded_mask_slow
    ), "Decoding mismatch between fast and slow versions"

    print(f"\nDecoding {mask_size} mask:")
    print(f"Fast version: {decoding_time:.4f} seconds")
    print(f"Slow version: {slow_time:.4f} seconds")
    print(f"Speedup: {slow_time/decoding_time:.1f}x")

    assert (
        decoding_time < expected_max_time
    ), f"Decoding took too long: {decoding_time:.4f} seconds"


def test_mask_roundtrip_correctness():
    """Test that encoding and then decoding a mask preserves the data exactly."""
    # Create a random mask
    test_mask = create_test_mask((500, 500))

    # Encode the mask
    rle = Mask.rle_encode(test_mask)

    # Create a mask instance
    mask = Mask(
        label="test",
        source="test",
        occluded=0,
        z_order=0,
        rle=rle,
        top=0,
        left=0,
        height=500,
        width=500,
        attributes=[],
    )

    # Decode the mask
    decoded_mask = mask.rle_decode()

    # Verify the decoded mask matches the original
    assert np.array_equal(test_mask, decoded_mask), "Decoded mask differs from original"


def test_fast_slow_equivalence():
    """Test that fast and slow versions produce identical results."""
    # Test different sizes to catch edge cases
    sizes = [(10, 10), (100, 100), (500, 500)]

    for size in sizes:
        # Create a random test mask
        test_mask = create_test_mask(size)

        # Test encoding
        fast_encoded = Mask.rle_encode(test_mask)
        slow_encoded = Mask.rle_encode_slow(test_mask)
        assert fast_encoded == slow_encoded, (
            f"Encoding mismatch for size {size}:\n"
            f"Fast: {fast_encoded}\n"
            f"Slow: {slow_encoded}"
        )

        # Create mask instance for decoding test
        mask = Mask(
            label="test",
            source="test",
            occluded=0,
            z_order=0,
            rle=fast_encoded,
            top=0,
            left=0,
            height=size[0],
            width=size[1],
            attributes=[],
        )

        # Test decoding
        fast_decoded = mask.rle_decode()
        slow_decoded = mask.rle_decode_slow()
        assert np.array_equal(fast_decoded, slow_decoded), (
            f"Decoding mismatch for size {size}:\n"
            f"Different elements: {np.sum(fast_decoded != slow_decoded)}"
        )


def test_edge_cases():
    """Test edge cases that might cause differences between fast and slow versions."""
    test_cases = [
        np.zeros((10, 10), dtype=bool),  # All zeros
        np.ones((10, 10), dtype=bool),  # All ones
        np.array([[True]]),  # Single pixel True
        np.array([[False]]),  # Single pixel False
        np.eye(10, dtype=bool),  # Diagonal pattern
    ]

    for test_case in test_cases:
        # Test encoding
        fast_encoded = Mask.rle_encode(test_case)
        slow_encoded = Mask.rle_encode_slow(test_case)
        assert fast_encoded == slow_encoded, (
            f"Encoding mismatch for case shape {test_case.shape}:\n"
            f"Fast: {fast_encoded}\n"
            f"Slow: {slow_encoded}"
        )

        # Create mask instance
        mask = Mask(
            label="test",
            source="test",
            occluded=0,
            z_order=0,
            rle=fast_encoded,
            top=0,
            left=0,
            height=test_case.shape[0],
            width=test_case.shape[1],
            attributes=[],
        )

        # Test decoding
        fast_decoded = mask.rle_decode()
        slow_decoded = mask.rle_decode_slow()
        assert np.array_equal(fast_decoded, slow_decoded), (
            f"Decoding mismatch for case shape {test_case.shape}:\n"
            f"Different elements: {np.sum(fast_decoded != slow_decoded)}"
        )
