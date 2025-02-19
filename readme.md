# Lithophane Generator

A Python script that converts 2D images into 3D printable lithophanes. This tool creates STL files optimized for translucent 3D printing, where the varying thickness of the material creates a visible image when backlit.

## Features

- Converts any image file into a 3D printable lithophane STL file
- Customizable thickness parameters for optimal contrast
- Maintains aspect ratio while scaling to desired dimensions
- Optional Gaussian smoothing to reduce noise
- Generates optimized mesh with proper face normals for 3D printing
- Creates a solid model with enclosed borders
- Configurable resolution and size settings

## Requirements

```
numpy
Pillow
numpy-stl
opencv-python
```

Install the required packages using:

```bash
pip install numpy Pillow numpy-stl opencv-python
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/lithophane-generator.git
cd lithophane-generator
```
## Usage

### Basic Usage

Convert an image to a lithophane with default settings:

```bash
python lithophane_generator.py input_image.jpg
```

This will create a file named `lithophane.stl` in the current directory.

### Advanced Usage

```bash
python lithophane_generator.py input_image.jpg \
    --output my_lithophane.stl \
    --max-thickness 4.0 \
    --min-thickness 0.8 \
    --width 150 \
    --no-smoothing
```

### Command Line Arguments

- `image`: Path to the input image file (required)
- `-o, --output`: Output STL file path (default: lithophane.stl)
- `--max-thickness`: Maximum thickness in mm for darker areas (default: 3.0)
- `--min-thickness`: Minimum thickness in mm for lighter areas (default: 0.6)
- `--width`: Desired width of the lithophane in mm (default: 100)
- `--no-smoothing`: Disable Gaussian smoothing (smoothing is enabled by default)

## Technical Details

### Algorithm Overview

1. **Image Processing**:
   - Converts input image to grayscale
   - Resizes while maintaining aspect ratio
   - Optionally applies Gaussian smoothing
   - Inverts image (darker pixels become thicker areas)

2. **Mesh Generation**:
   - Creates a front surface with varying thickness based on pixel values
   - Generates a flat back surface
   - Constructs border faces to create a solid model
   - Optimizes face normal directions for 3D printing

3. **Output**:
   - Generates an STL file compatible with all major 3D printing slicers
   - Uses binary STL format for efficiency

### Resolution and Scale

- Default resolution is approximately 0.2mm per pixel
- Final dimensions are determined by the specified width parameter
- Height is automatically calculated to maintain the original aspect ratio

## Printing Recommendations

For best results when 3D printing:

1. **Material Selection**:
   - Use translucent or white filament (PLA, PETG, or ABS)
   - Light-colored filaments generally produce better results

2. **Print Settings**:
   - Layer height: 0.1-0.16mm
   - 100% infill
   - 2-3 perimeter walls
   - Print with the flat side down
   - No support structures needed

3. **Display Setup**:
   - Use LED backlighting
   - Maintain consistent lighting across the entire surface
   - Optimal viewing distance varies with size

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCV for image processing capabilities
- numpy-stl for STL file generation
- Pillow for image handling

## Known Issues

1. Very high-resolution images may require significant processing time
2. Memory usage scales with image resolution
3. Extremely low-contrast images may produce subtle lithophanes

Please report any bugs or feature requests through the issue tracker.
