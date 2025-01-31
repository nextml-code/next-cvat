from pathlib import Path
from xml.etree import ElementTree

import numpy as np
import pytest

from next_cvat import Annotations
from next_cvat.types import Attribute, Ellipse, ImageAnnotation


def test_ellipse_annotations(tmp_path):
    """Test that ellipse annotations are correctly parsed and saved."""
    # Create a test annotations XML
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<annotations>
  <version>1.1</version>
  <meta>
    <project>
      <id>1</id>
      <name>Test Project</name>
      <created>2024-01-01 12:00:00.000000+00:00</created>
      <updated>2024-01-01 12:00:00.000000+00:00</updated>
      <labels>
        <label>
          <name>Deformation</name>
          <color>#ff0000</color>
          <type>any</type>
        </label>
      </labels>
    </project>
  </meta>
  <image id="1" name="test.jpg" width="4096" height="1024">
    <ellipse label="Deformation" source="manual" occluded="0" cx="3126.92" cy="509.86" rx="39.99" ry="18.92" z_order="0">
      <attribute name="Damage Level">0</attribute>
      <attribute name="Corrugation">false</attribute>
    </ellipse>
  </image>
</annotations>"""
    xml_path = tmp_path / "annotations.xml"
    xml_path.write_text(xml_content)

    # Load annotations
    annotations = Annotations.from_path(xml_path)

    # Verify ellipse was loaded correctly
    assert len(annotations.images) == 1
    image = annotations.images[0]
    assert len(image.ellipses) == 1
    ellipse = image.ellipses[0]

    # Check ellipse properties
    assert ellipse.label == "Deformation"
    assert ellipse.source == "manual"
    assert ellipse.occluded == 0
    assert ellipse.cx == 3126.92
    assert ellipse.cy == 509.86
    assert ellipse.rx == 39.99
    assert ellipse.ry == 18.92
    assert ellipse.z_order == 0

    # Check attributes
    assert len(ellipse.attributes) == 2
    damage_level = next(
        attr for attr in ellipse.attributes if attr.name == "Damage Level"
    )
    assert damage_level.value == "0"
    corrugation = next(
        attr for attr in ellipse.attributes if attr.name == "Corrugation"
    )
    assert corrugation.value == "false"

    # Test saving and reloading
    output_path = tmp_path / "output.xml"
    annotations.save_xml_(output_path)

    # Reload and verify
    reloaded = Annotations.from_path(output_path)
    assert len(reloaded.images) == 1
    reloaded_image = reloaded.images[0]
    assert len(reloaded_image.ellipses) == 1
    reloaded_ellipse = reloaded_image.ellipses[0]

    # Verify all properties are preserved
    assert reloaded_ellipse.model_dump() == ellipse.model_dump()


def test_ellipse_creation():
    """Test creating ellipse annotations programmatically."""
    # Create an ellipse
    ellipse = Ellipse(
        label="Deformation",
        source="manual",
        occluded=0,
        cx=100.0,
        cy=200.0,
        rx=30.0,
        ry=15.0,
        z_order=0,
        attributes=[
            Attribute(name="Damage Level", value="1"),
            Attribute(name="Corrugation", value="true"),
        ],
    )

    # Create an image annotation with the ellipse
    image = ImageAnnotation(
        id="1",
        name="test.jpg",
        width=800,
        height=600,
        ellipses=[ellipse],
    )

    # Verify ellipse properties
    assert len(image.ellipses) == 1
    saved_ellipse = image.ellipses[0]
    assert saved_ellipse.cx == 100.0
    assert saved_ellipse.cy == 200.0
    assert saved_ellipse.rx == 30.0
    assert saved_ellipse.ry == 15.0
    assert len(saved_ellipse.attributes) == 2


def test_ellipse_to_polygon():
    """Test converting ellipse to polygon approximation."""
    ellipse = Ellipse(
        label="test",
        cx=100.0,
        cy=100.0,
        rx=50.0,
        ry=25.0,
        z_order=0,
    )

    # Convert to polygon with default number of points
    poly = ellipse.polygon()
    assert len(poly.points) == 32  # Default number of points
    assert poly.label == ellipse.label
    assert poly.z_order == ellipse.z_order

    # Test with custom number of points
    poly = ellipse.polygon(num_points=16)
    assert len(poly.points) == 16

    # Verify points lie on the ellipse
    for x, y in poly.points:
        # Points should satisfy the ellipse equation approximately
        # ((x-h)/rx)^2 + ((y-k)/ry)^2 ≈ 1
        dist = ((x - ellipse.cx) / ellipse.rx) ** 2 + (
            (y - ellipse.cy) / ellipse.ry
        ) ** 2
        assert abs(dist - 1.0) < 1e-10


def test_ellipse_segmentation():
    """Test creating segmentation mask from ellipse."""
    ellipse = Ellipse(
        label="test",
        cx=50.0,
        cy=30.0,
        rx=20.0,
        ry=10.0,
        z_order=0,
    )

    # Create segmentation mask
    height, width = 60, 100
    mask = ellipse.segmentation(height=height, width=width)

    # Check mask properties
    assert mask.shape == (height, width)
    assert mask.dtype == bool

    # Center point should be True
    assert mask[30, 50]  # cy, cx

    # Points far outside should be False
    assert not mask[0, 0]  # Top-left corner
    assert not mask[-1, -1]  # Bottom-right corner

    # Check approximate area
    # Ellipse area should be approximately pi * rx * ry
    expected_area = np.pi * ellipse.rx * ellipse.ry
    actual_area = np.sum(mask)
    assert abs(actual_area - expected_area) / expected_area < 0.1  # Within 10%
