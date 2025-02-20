import numpy as np
from PIL import Image
from stl import mesh
import cv2
import argparse
from tqdm import tqdm
import os
from pathlib import Path

def create_side_walls(vertices, faces, rows, cols, row_offset):
    """Add side walls to make the model solid and printable"""
    
    # Front wall
    for col in range(cols - 1):
        v1 = col
        v2 = col + 1
        b1 = row_offset + col
        b2 = row_offset + col + 1
        faces.extend([
            [v1, v2, b1],
            [b1, v2, b2]
        ])
    
    # Back wall
    for col in range(cols - 1):
        v1 = (rows - 1) * cols + col
        v2 = (rows - 1) * cols + col + 1
        b1 = row_offset + (rows - 1) * cols + col
        b2 = row_offset + (rows - 1) * cols + col + 1
        faces.extend([
            [v1, b1, v2],
            [b1, b2, v2]
        ])
    
    # Left wall
    for row in range(rows - 1):
        v1 = row * cols
        v2 = (row + 1) * cols
        b1 = row_offset + row * cols
        b2 = row_offset + (row + 1) * cols
        faces.extend([
            [v1, b1, v2],
            [b1, b2, v2]
        ])
    
    # Right wall
    for row in range(rows - 1):
        v1 = row * cols + (cols - 1)
        v2 = (row + 1) * cols + (cols - 1)
        b1 = row_offset + row * cols + (cols - 1)
        b2 = row_offset + (row + 1) * cols + (cols - 1)
        faces.extend([
            [v1, v2, b1],
            [b1, v2, b2]
        ])
    return faces

def add_border_frame(vertices, faces, rows, cols, border_width, border_height, base_height, scale_x, scale_y):
    """Add decorative border frame around the lithophane"""
    original_vertex_count = len(vertices)
    
    # Calculate actual model dimensions
    model_width = (cols - 1) * scale_x
    model_height = (rows - 1) * scale_y
    
    # Add frame vertices
    frame_vertices = []
    
    # Create vertices for a full border frame
    # Top face vertices
    frame_vertices.extend([
        [-border_width, -border_width, border_height],  # Top-left (0)
        [model_width + border_width, -border_width, border_height],  # Top-right (1)
        [model_width + border_width, model_height + border_width, border_height],  # Bottom-right (2)
        [-border_width, model_height + border_width, border_height],  # Bottom-left (3)
        
        # Inner top vertices
        [0, 0, border_height],  # Inner top-left (4)
        [model_width, 0, border_height],  # Inner top-right (5)
        [model_width, model_height, border_height],  # Inner bottom-right (6)
        [0, model_height, border_height],  # Inner bottom-left (7)
    ])
    
    # Bottom face vertices
    frame_vertices.extend([
        [-border_width, -border_width, 0],  # Bottom face top-left (8)
        [model_width + border_width, -border_width, 0],  # Bottom face top-right (9)
        [model_width + border_width, model_height + border_width, 0],  # Bottom face bottom-right (10)
        [-border_width, model_height + border_width, 0],  # Bottom face bottom-left (11)
        
        # Inner bottom vertices
        [0, 0, 0],  # Inner bottom top-left (12)
        [model_width, 0, 0],  # Inner bottom top-right (13)
        [model_width, model_height, 0],  # Inner bottom bottom-right (14)
        [0, model_height, 0],  # Inner bottom bottom-left (15)
    ])
    
    vertices.extend(frame_vertices)
    base_idx = original_vertex_count
    
    # Create faces for the border frame
    frame_faces = []
    
    # Top surface faces (between outer and inner border)
    for i in range(4):
        next_i = (i + 1) % 4
        inner_i = i + 4
        inner_next = ((i + 1) % 4) + 4
        
        frame_faces.extend([
            [base_idx + i, base_idx + next_i, base_idx + inner_i],
            [base_idx + next_i, base_idx + inner_next, base_idx + inner_i]
        ])
    
    # Bottom surface faces
    for i in range(4):
        next_i = (i + 1) % 4
        inner_i = i + 12
        inner_next = ((i + 1) % 4) + 12
        
        frame_faces.extend([
            [base_idx + i + 8, base_idx + inner_i, base_idx + next_i + 8],
            [base_idx + next_i + 8, base_idx + inner_i, base_idx + inner_next]
        ])
    
    # Outer wall faces
    for i in range(4):
        next_i = (i + 1) % 4
        frame_faces.extend([
            [base_idx + i, base_idx + i + 8, base_idx + next_i],
            [base_idx + next_i, base_idx + i + 8, base_idx + next_i + 8]
        ])
    
    # Inner wall faces
    for i in range(4):
        next_i = (i + 1) % 4
        frame_faces.extend([
            [base_idx + i + 4, base_idx + next_i + 4, base_idx + i + 12],
            [base_idx + next_i + 4, base_idx + next_i + 12, base_idx + i + 12]
        ])
    
    faces.extend(frame_faces)
    return vertices, faces

def create_lithophane(image_path, output_path, max_thickness=3.0, min_thickness=0.6, 
                     width=100, smoothing=True, border=False, border_width=5, 
                     border_height=5, invert=False):
    """
    Convert an image to a lithophane STL with enhanced features.
    
    Args:
        image_path (str): Path to input image
        output_path (str): Path for output STL file
        max_thickness (float): Maximum thickness in mm (darker areas)
        min_thickness (float): Minimum thickness in mm (lighter areas)
        width (int): Desired width in mm
        smoothing (bool): Apply Gaussian smoothing
        border (bool): Add decorative border
        border_width (float): Width of border in mm
        border_height (float): Height of border in mm
        invert (bool): Invert the thickness mapping
    """
    # Validate input file
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(os.path.abspath(output_path))
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("Loading and processing image...")
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Could not read image - file may be corrupted")
    
    # Calculate dimensions
    aspect_ratio = img.shape[1] / img.shape[0]
    new_width = int(width / 0.2)
    new_height = int(new_width / aspect_ratio)
    
    # Resize image
    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
    if smoothing:
        img = cv2.GaussianBlur(img, (3, 3), 0)

    if not invert:
        img = 255 - img
    
    # Convert pixel values to thickness
    thicknesses = (img.astype(float) / 255.0) * (max_thickness - min_thickness) + min_thickness
    
    # Initialize progress bar
    total_steps = new_height * new_width * 2
    pbar = tqdm(total=total_steps, desc="Generating 3D mesh")

    # Create vertices and faces
    rows, cols = thicknesses.shape
    vertices = []
    faces = []
    
    # Scale factors
    scale_x = width / (cols - 1)
    scale_y = (width / aspect_ratio) / (rows - 1)

    # Create vertices for flat lithophane
    for row in range(rows):
        for col in range(cols):
            vertices.append([col * scale_x, row * scale_y, thicknesses[row, col]])
            pbar.update(1)

    # Create back vertices
    for row in range(rows):
        for col in range(cols):
            vertices.append([col * scale_x, row * scale_y, 0])
            pbar.update(1)
    pbar.set_description("Creating faces")

    for row in range(rows - 1):
        for col in range(cols - 1):
            v1 = row * cols + col
            v2 = row * cols + (col + 1)
            v3 = (row + 1) * cols + col
            v4 = (row + 1) * cols + (col + 1)
            
            faces.append([v1, v3, v2])
            faces.append([v2, v3, v4])
            
            b1 = rows * cols + row * cols + col
            b2 = rows * cols + row * cols + (col + 1)
            b3 = rows * cols + (row + 1) * cols + col
            b4 = rows * cols + (row + 1) * cols + (col + 1)
            
            faces.append([b1, b2, b3])
            faces.append([b2, b4, b3])
    
    # Add side walls
    pbar.set_description("Adding side walls")
    faces = create_side_walls(vertices, faces, rows, cols, rows * cols)
    
    # Add border if requested
    if border:
        pbar.set_description("Adding border frame")
        vertices, faces = add_border_frame(vertices, faces, rows, cols, 
                                         border_width, border_height, 
                                         min_thickness, scale_x, scale_y)
    
    # Create the mesh
    pbar.set_description("Finalizing mesh")
    vertices = np.array(vertices)
    faces = np.array(faces)
    
    model = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            model.vectors[i][j] = vertices[face[j]]
    
    pbar.set_description("Saving STL file")
    try:
        model.save(output_path)
    except Exception as e:
        raise RuntimeError(f"Failed to save STL file: {str(e)}")
    
    pbar.close()
    
    print(f"Lithophane creation complete!")
    print(f"Output file: {output_path}")
    print(f"Model dimensions: {width}mm x {width/aspect_ratio:.1f}mm")
    print(f"Thickness range: {min_thickness}mm to {max_thickness}mm")
    if border:
        print(f"Border added: {border_width}mm wide, {border_height}mm high")


def main():
    parser = argparse.ArgumentParser(description='Convert an image to a lithophane STL file')
    parser.add_argument('image', help='Path to the input image file')
    parser.add_argument('-o', '--output', help='Output STL file path (default: lithophane.stl)', 
                        default='lithophane.stl')
    parser.add_argument('--max-thickness', '-mxt', type=float, 
                        help='Maximum thickness in mm (default: 3.0)', default=3.0)
    parser.add_argument('--min-thickness', '-mnt', type=float, 
                        help='Minimum thickness in mm (default: 0.6)', default=0.6)
    parser.add_argument('--width', '-w', type=int, 
                        help='Width in mm (default: 100)', default=100)
    parser.add_argument('--no-smoothing', action='store_true', 
                        help='Disable smoothing')
    parser.add_argument('--border', action='store_true', 
                        help='Add decorative border')
    parser.add_argument('--border-width', '-bw', type=float, 
                        help='Border width in mm (default: 5)', default=5)
    parser.add_argument('--border-height', '-bh', type=float, 
                        help='Border height in mm (default: 5)', default=5)
    parser.add_argument('--invert', action='store_true', 
                        help='Invert thickness mapping')

    args = parser.parse_args()
    
    try:
        create_lithophane(
            image_path=args.image,
            output_path=args.output,
            max_thickness=args.max_thickness,
            min_thickness=args.min_thickness,
            width=args.width,
            smoothing=not args.no_smoothing,
            border=args.border,
            border_width=args.border_width,
            border_height=args.border_height,
            invert=args.invert
        )
    except Exception as e:
        print(f"\nError: {str(e)}")
        parser.print_help()
        exit(1)

if __name__ == "__main__":
    main()