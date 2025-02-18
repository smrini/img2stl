import numpy as np
from PIL import Image
from stl import mesh
import cv2
import argparse

def create_lithophane(image_path, output_path, max_thickness=3.0, min_thickness=0.6, width=100, smoothing=True):
    """
    Convert an image to a lithophane STL optimized for translucent printing.
    
    Args:
        image_path (str): Path to input image
        output_path (str): Path for output STL file
        max_thickness (float): Maximum thickness in mm (darker areas)
        min_thickness (float): Minimum thickness in mm (lighter areas)
        width (int): Desired width in mm
        smoothing (bool): Apply Gaussian smoothing to reduce noise
    """
    # Read and convert image to grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Could not read image")
    
    # Calculate aspect ratio and new dimensions
    aspect_ratio = img.shape[1] / img.shape[0]
    new_width = int(width / 0.2)  # 0.2mm per pixel resolution
    new_height = int(new_width / aspect_ratio)
    
    # Resize image
    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Apply smoothing if requested
    if smoothing:
        img = cv2.GaussianBlur(img, (3, 3), 0)
    
    # Invert image (darker areas should be thicker)
    img = 255 - img
    
    # Convert pixel values to thickness
    thicknesses = (img.astype(float) / 255.0) * (max_thickness - min_thickness) + min_thickness
    
    # Create vertices and faces
    rows, cols = thicknesses.shape
    vertices = []
    faces = []
    
    # Scale factors for final size
    scale_x = width / cols
    scale_y = (width / aspect_ratio) / rows
    
    # Create front vertices
    for row in range(rows):
        for col in range(cols):
            x = col * scale_x
            y = row * scale_y
            z = thicknesses[row, col]
            vertices.append([x, y, z])
    
    # Create back vertices (flat surface)
    for row in range(rows):
        for col in range(cols):
            vertices.append([col * scale_x, row * scale_y, 0])
    
    # Create faces (similar to previous script but optimized for lithophane)
    # Front faces
    for row in range(rows - 1):
        for col in range(cols - 1):
            # Front surface triangles
            v1 = row * cols + col
            v2 = row * cols + (col + 1)
            v3 = (row + 1) * cols + col
            v4 = (row + 1) * cols + (col + 1)
            
            faces.append([v1, v3, v2])  # Note: reversed for correct normal direction
            faces.append([v2, v3, v4])
            
            # Back surface triangles
            b1 = rows * cols + row * cols + col
            b2 = rows * cols + row * cols + (col + 1)
            b3 = rows * cols + (row + 1) * cols + col
            b4 = rows * cols + (row + 1) * cols + (col + 1)
            
            faces.append([b1, b2, b3])
            faces.append([b2, b4, b3])
    
    # Add border faces
    def add_border_faces(vertices, faces, rows, cols):
        # Left border
        for row in range(rows - 1):
            v1 = row * cols
            v2 = (row + 1) * cols
            b1 = rows * cols + row * cols
            b2 = rows * cols + (row + 1) * cols
            faces.extend([[v1, b1, v2], [b1, b2, v2]])
        
        # Right border
        for row in range(rows - 1):
            v1 = row * cols + (cols - 1)
            v2 = (row + 1) * cols + (cols - 1)
            b1 = rows * cols + row * cols + (cols - 1)
            b2 = rows * cols + (row + 1) * cols + (cols - 1)
            faces.extend([[v1, v2, b1], [b1, v2, b2]])
        
        # Top border
        for col in range(cols - 1):
            v1 = col
            v2 = col + 1
            b1 = rows * cols + col
            b2 = rows * cols + col + 1
            faces.extend([[v1, v2, b1], [b1, v2, b2]])
        
        # Bottom border
        for col in range(cols - 1):
            v1 = (rows - 1) * cols + col
            v2 = (rows - 1) * cols + col + 1
            b1 = rows * cols + (rows - 1) * cols + col
            b2 = rows * cols + (rows - 1) * cols + col + 1
            faces.extend([[v1, b1, v2], [b1, b2, v2]])
    
    add_border_faces(vertices, faces, rows, cols)
    
    # Create the mesh
    vertices = np.array(vertices)
    faces = np.array(faces)
    
    # Create the mesh object
    model = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    
    # Add vertices for each face
    for i, face in enumerate(faces):
        for j in range(3):
            model.vectors[i][j] = vertices[face[j]]
    
    # Save the mesh to STL file
    model.save(output_path)
    print(f"Created lithophane: {output_path}")
    print(f"Model dimensions: {width}mm x {width/aspect_ratio:.1f}mm")
    print(f"Thickness range: {min_thickness}mm to {max_thickness}mm")

def main():
    parser = argparse.ArgumentParser(description='Convert an image to a lithophane STL file')
    parser.add_argument('image', help='Path to the input image file')
    parser.add_argument('-o', '--output', help='Output STL file path (default: lithophane.stl)', default='lithophane.stl')
    parser.add_argument('--max-thickness', type=float, help='Maximum thickness in mm (default: 3.0)', default=3.0)
    parser.add_argument('--min-thickness', type=float, help='Minimum thickness in mm (default: 0.6)', default=0.6)
    parser.add_argument('--width', type=int, help='Width in mm (default: 100)', default=100)
    parser.add_argument('--no-smoothing', action='store_true', help='Disable smoothing')
    
    args = parser.parse_args()
    
    try:
        create_lithophane(
            image_path=args.image,
            output_path=args.output,
            max_thickness=args.max_thickness,
            min_thickness=args.min_thickness,
            width=args.width,
            smoothing=not args.no_smoothing
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        parser.print_help()

if __name__ == "__main__":
    main()