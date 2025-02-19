# Lithophane Generator

A Python script that converts 2D images into 3D printable lithophanes. This tool creates STL files optimized for translucent 3D printing, where the varying thickness of the material creates a visible image when backlit.

## Features

- Converts any image file into a 3D printable lithophane STL file
- Customizable thickness parameters for optimal contrast
- Maintains aspect ratio while scaling to desired dimensions
- Optional Gaussian smoothing to reduce noise
- Generates optimized mesh with proper face normals for 3D printing
- Creates a solid model with enclosed borders
- Optional decorative border frame
- Configurable resolution and size settings
- Image inversion option for different lighting setups

## Requirements

```
numpy
Pillow
numpy-stl
opencv-python
tqdm
```

Install the required packages using:

```bash
pip install numpy Pillow numpy-stl opencv-python tqdm
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

### Advanced Usage Examples

1. Basic lithophane with custom dimensions:
```bash
python lithophane_generator.py input_image.jpg -output my_lithophane.stl --width 150
```

2. High contrast lithophane with thicker walls:
```bash
python lithophane_generator.py input_image.jpg --max-thickness 4.0 --min-thickness 0.8 --width 100 --no-smoothing
```

3. Lithophane with decorative border:
```bash
python lithophane_generator.py input_image.jpg --border --border-width 8 --border-height 6
```

4. Inverted lithophane for different lighting setups:
```bash
python lithophane_generator.py input_image.jpg --invert --max-thickness 3.5 --min-thickness 0.5
```

5. Fine-tuned lithophane for detailed images:
```bash
python lithophane_generator.py input_image.jpg --width 200 --max-thickness 2.5 --min-thickness 0.4 --border --border-width 5 --border-height 4
```
### PNG images support
The script also supports PNG images. However, due to limitations in the Pillow library, the alpha channel is not supported. This means that the script will ignore the alpha channel in the input image and treat the image as a 3-channel RGB image.
In other words, the script will replace the transparent pixels with a flat surface.

### Command Line Arguments

- `image`: Path to the input image file (required)
- `-o, --output`: Output STL file path (default: lithophane.stl)
- `-mxt, --max-thickness`: Maximum thickness in mm for darker areas (default: 3.0)
- `-mnt, --min-thickness`: Minimum thickness in mm for lighter areas (default: 0.6)
- `-w, --width`: Desired width of the lithophane in mm (default: 100)
- `--no-smoothing`: Disable Gaussian smoothing (smoothing is enabled by default)
- `--border`: Add decorative border frame around the lithophane
- `-bw, --border-width`: Width of the border in mm (default: 5)
- `-bh, --border-height`: Height of the border in mm (default: 5)
- `--invert`: Invert the thickness mapping for different lighting setups

## Technical Details

### Algorithm Overview

1. **Image Processing**:
   - Converts input image to grayscale
   - Resizes while maintaining aspect ratio
   - Optionally applies Gaussian smoothing
   - Optionally inverts image for different lighting setups
   - Maps pixel values to thickness range

2. **Mesh Generation**:
   - Creates a front surface with varying thickness based on pixel values
   - Generates a flat back surface
   - Constructs border faces to create a solid model
   - Optionally adds decorative border frame
   - Optimizes face normal directions for 3D printing

3. **Output**:
   - Generates an STL file compatible with all major 3D printing slicers
   - Uses binary STL format for efficiency
   - Provides progress feedback during generation
   - creates the specified directory if it doesn't exist

### Resolution and Scale

- Resolution is automatically calculated based on the desired width
- Default resolution is approximately 0.2mm per pixel
- Final dimensions are determined by the specified width parameter
- Height is automatically calculated to maintain the original aspect ratio
- Border dimensions can be customized independently

## Printing Recommendations

For best results when 3D printing:

1. **Material Selection**:
   - Use translucent or white filament (PLA, PETG, or ABS)
   - Light-colored filaments generally produce better results
   - Consider using transparent PETG for maximum light transmission

2. **Print Settings**:
   - Layer height: 0.1-0.16mm
   - 100% infill
   - 2-3 perimeter walls
   - Print with the flat side down
   - No support structures needed

3. **Display Setup**:
   - Use LED backlighting (warm or cool white depending on preference)
   - Maintain consistent lighting across the entire surface
   - Optimal viewing distance varies with size
   - Consider using diffused lighting for more even illumination

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCV for image processing capabilities
- numpy-stl for STL file generation
- Pillow for image handling
- tqdm for progress visualization

## Known Issues

1. Very high-resolution images may require significant processing time
2. Low-resolution images may result in less detailed lithophanes
3. Memory usage scales with image resolution
4. Extremely low-contrast images may produce subtle lithophanes
5. Border generation may increase processing time for large models

## Future Improvements

1. Adding more decorative borders
2. Adding curved stl files option
3. Adding support for more image formats

## Troubleshooting

1. If the output appears inverted, try using the `--invert` flag
2. For better detail in dark areas, increase `max-thickness`
3. For more delicate highlights, decrease `min-thickness`
4. If the model appears too rough, ensure smoothing is enabled (default)
5. For faster processing of large images, consider reducing the width parameter

Please report any bugs or feature requests through the issue tracker.