#!/usr/bin/env python
"""
Batch RGB Generator for PACE HARP2 L1B Data

This script generates multiple RGB combinations from HARP2 L1B data using different
view angle combinations to explore various atmospheric and surface features.

Created by Anin Puthukkudy (ESI, UMBC)
"""

import os
import sys
import argparse
from pathlib import Path
import subprocess
import time

# Import the RGB creation function
import importlib.util
import sys

# Load the L1B-RGB-example module dynamically
spec = importlib.util.spec_from_file_location("l1b_rgb", "L1B-RGB-example.py")
l1b_rgb_module = importlib.util.module_from_spec(spec)
sys.modules["l1b_rgb"] = l1b_rgb_module
spec.loader.exec_module(l1b_rgb_module)

# Import the function
create_l1b_rgb = l1b_rgb_module.create_l1b_rgb

# Manually defined RGB combinations based on viewing angle indices
RGB_COMBINATIONS = {
    "p20": {"angles": [31, 3, 83], "description": "Manual combination 1"},
    "p8": {"angles": [36, 4, 84], "description": "Manual combination 2"},
    "p34": {"angles": [25, 2, 82], "description": "Manual combination 3"},
    "p44": {"angles": [18, 1, 81], "description": "Manual combination 4"},
    "p55": {"angles": [10, 0, 80], "description": "Manual combination 5"},
    "n55": {"angles": [69, 9, 89], "description": "Manual combination 6"},
    "n44": {"angles": [60, 8, 88], "description": "Manual combination 7"},
    "n33": {"angles": [53, 7, 87], "description": "Manual combination 8"},
    "n20": {"angles": [48, 6, 86], "description": "Manual combination 9"},
    "n6": {"angles": [41, 5, 85], "description": "Manual combination 10"},
}


def validate_file(filepath):
    """Validate that the input file exists and is a NetCDF file"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file not found: {filepath}")

    if not filepath.lower().endswith(".nc"):
        print(f"Warning: File doesn't appear to be NetCDF: {filepath}")

    return True


def create_output_directory(base_path, filename):
    """Create output directory structure"""
    base_filename = os.path.splitext(os.path.basename(filename))[0]
    output_dir = os.path.join(base_path, f"{base_filename}_RGB_batch")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def stitch_l1b_data(filenames, variable="i"):
    """
    Stitch multiple L1B files together

    Args:
        filenames (list): List of L1B file paths in order
        variable (str): Variable to extract

    Returns:
        dict: Stitched L1B data dictionary
    """
    from nasa_pace_data_reader import L1
    import numpy as np

    print(f"Stitching {len(filenames)} L1B files...")

    all_data = []
    all_lats = []
    all_lons = []
    metadata = None

    for i, filename in enumerate(filenames):
        print(f"  Reading file {i+1}/{len(filenames)}: {os.path.basename(filename)}")

        l1b = L1.L1B()
        l1b_dict = l1b.read(filename)

        # Store metadata from first file
        if metadata is None:
            metadata = {
                key: val
                for key, val in l1b_dict.items()
                if key not in [variable, "latitude", "longitude"]
            }

        # Extract data for stitching (use float32 for processing speed)
        data = l1b_dict[variable].astype(np.float32)  # Shape: (angles, y, x)
        lats = l1b_dict["latitude"].astype(np.float32)  # Shape: (angles, y, x)
        lons = l1b_dict["longitude"].astype(np.float32)  # Shape: (angles, y, x)

        all_data.append(data)
        all_lats.append(lats)
        all_lons.append(lons)

    # Stitch along the appropriate axis (assuming along-track stitching - axis=1)
    print("  Stitching data arrays...")
    stitched_data = np.concatenate(
        all_data, axis=1
    )  # Stitch along y-axis (along-track)
    stitched_lats = np.concatenate(all_lats, axis=1)
    stitched_lons = np.concatenate(all_lons, axis=1)

    print(f"  Stitched shape: {stitched_data.shape}")

    # Create stitched dictionary
    stitched_dict = metadata.copy()
    stitched_dict[variable] = stitched_data
    stitched_dict["latitude"] = stitched_lats
    stitched_dict["longitude"] = stitched_lons

    return stitched_dict


def create_l1b_rgb_from_dict(
    l1b_dict,
    temp_filename,
    output_dir,
    view_angles,
    norm_factor=300,
    variable="i",
    save_fig=True,
    save_geotiff=False,
    save_kmz=False,
    fixed_grid=False,
    grid_resolution=0.03,
    grid_extent=None,
):
    """
    Create RGB from L1B data dictionary using the main create_l1b_rgb function

    Args:
        l1b_dict: L1B data dictionary
        temp_filename: Temporary filename for the create_l1b_rgb function
        output_dir: Output directory
        view_angles: List of 3 view angle indices
        norm_factor: Normalization factor
        variable: Variable to plot
        save_fig: Save PNG
        save_geotiff: Save GeoTIFF
        save_kmz: Save KMZ
        fixed_grid: Use fixed regular grid
        grid_resolution: Grid resolution in degrees
        grid_extent: Grid extent specification

    Returns:
        dict: Results
    """
    # Monkey patch the L1B reader to use our stitched data
    import numpy as np
    from matplotlib import pyplot as plt
    from nasa_pace_data_reader import L1

    # Get data dimensions
    data_shape = l1b_dict[variable].shape
    print(f"    Data shape: {data_shape}")

    # Store original L1B read method
    original_read = L1.L1B.read

    # Create a monkey patch that returns our stitched data
    def patched_read(self, filename):
        return l1b_dict

    # Apply monkey patch
    L1.L1B.read = patched_read

    try:
        # Call the main create_l1b_rgb function
        result = create_l1b_rgb(
            filename=temp_filename,
            output_dir=output_dir,
            view_angles=view_angles,
            norm_factor=norm_factor,
            variable=variable,
            save_fig=save_fig,
            show_plot=False,
            save_geotiff=save_geotiff,
            save_kmz=save_kmz,
            fixed_grid=fixed_grid,
            grid_resolution=grid_resolution,
            grid_extent=grid_extent,
        )

        return result

    finally:
        # Restore original read method
        L1.L1B.read = original_read


def export_geotiff(
    rgb_data, ref_lat, ref_lon, base_filename, view_angles, variable, output_dir
):
    """Export RGB data as GeoTIFF with transparency"""
    try:
        import rasterio
        from rasterio.crs import CRS
        from pyresample import geometry, kd_tree
        import numpy as np

        geotiff_file = os.path.join(
            output_dir,
            f"{base_filename}_L1B_RGB_{variable}_angles_{view_angles[0]}_{view_angles[1]}_{view_angles[2]}.tif",
        )

        # Get data bounds
        lat_min, lat_max = np.nanmin(ref_lat), np.nanmax(ref_lat)
        lon_min, lon_max = np.nanmin(ref_lon), np.nanmax(ref_lon)

        # Create regular grid
        grid_size = min(ref_lat.shape)
        lats_reg = np.linspace(lat_min, lat_max, grid_size, dtype=np.float32)
        lons_reg = np.linspace(lon_min, lon_max, grid_size, dtype=np.float32)
        lon_grid_reg, lat_grid_reg = np.meshgrid(lons_reg, lats_reg)

        # Resample to regular grid
        source_def = geometry.SwathDefinition(lons=ref_lon, lats=ref_lat)
        target_def = geometry.GridDefinition(lons=lon_grid_reg, lats=lat_grid_reg)

        rgb_regular = np.zeros((grid_size, grid_size, 3), dtype=np.float32)
        for i in range(3):
            rgb_regular[:, :, i] = kd_tree.resample_nearest(
                source_def,
                rgb_data[:, :, i],
                target_def,
                radius_of_influence=10000,
                fill_value=0,
            )

        # Create alpha channel
        alpha_channel = np.ones((grid_size, grid_size), dtype=np.uint8) * 255
        missing_data_mask = np.any(rgb_regular <= 0, axis=2)
        alpha_channel[missing_data_mask] = 0

        # Convert to uint8
        rgb_uint8 = (rgb_regular * 255).astype(np.uint8)

        # Create transform
        transform_matrix = rasterio.transform.from_bounds(
            lon_min, lat_min, lon_max, lat_max, grid_size, grid_size
        )

        # Write GeoTIFF
        with rasterio.open(
            geotiff_file,
            "w",
            driver="GTiff",
            height=grid_size,
            width=grid_size,
            count=4,
            dtype=rgb_uint8.dtype,
            crs=CRS.from_epsg(4326),
            transform=transform_matrix,
            compress="lzw",
        ) as dst:
            for i in range(3):
                dst.write(np.flipud(rgb_uint8[:, :, i]), i + 1)
            dst.write(np.flipud(alpha_channel), 4)

        print(f"    GeoTIFF saved to: {geotiff_file}")

    except Exception as e:
        print(f"    Warning: GeoTIFF export failed: {e}")


def export_kmz(
    rgb_data, ref_lat, ref_lon, base_filename, view_angles, variable, output_dir
):
    """Export RGB data as KMZ"""
    try:
        import zipfile
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom import minidom
        from pyresample import geometry, kd_tree
        import numpy as np
        from matplotlib import pyplot as plt

        kmz_file = os.path.join(
            output_dir,
            f"{base_filename}_L1B_RGB_{variable}_angles_{view_angles[0]}_{view_angles[1]}_{view_angles[2]}.kmz",
        )
        png_name = f"L1B_RGB_{variable}.png"

        # Get bounds and create regular grid (same as GeoTIFF)
        lat_min, lat_max = np.nanmin(ref_lat), np.nanmax(ref_lat)
        lon_min, lon_max = np.nanmin(ref_lon), np.nanmax(ref_lon)

        grid_size = min(ref_lat.shape)
        lats_reg = np.linspace(lat_min, lat_max, grid_size, dtype=np.float32)
        lons_reg = np.linspace(lon_min, lon_max, grid_size, dtype=np.float32)
        lon_grid_reg, lat_grid_reg = np.meshgrid(lons_reg, lats_reg)

        # Resample to regular grid
        source_def = geometry.SwathDefinition(lons=ref_lon, lats=ref_lat)
        target_def = geometry.GridDefinition(lons=lon_grid_reg, lats=lat_grid_reg)

        rgb_regular = np.zeros((grid_size, grid_size, 3), dtype=np.float32)
        for i in range(3):
            rgb_regular[:, :, i] = kd_tree.resample_nearest(
                source_def,
                rgb_data[:, :, i],
                target_def,
                radius_of_influence=10000,
                fill_value=0,
            )

        # Create KML
        kml = Element("kml", xmlns="http://www.opengis.net/kml/2.2")
        document = SubElement(kml, "Document")
        name = SubElement(document, "name")
        name.text = f"L1B RGB {variable.upper()}"

        ground_overlay = SubElement(document, "GroundOverlay")
        overlay_name = SubElement(ground_overlay, "name")
        overlay_name.text = f"L1B RGB - View Angles: {view_angles}"

        icon = SubElement(ground_overlay, "Icon")
        href = SubElement(icon, "href")
        href.text = png_name

        latlonbox = SubElement(ground_overlay, "LatLonBox")
        north = SubElement(latlonbox, "north")
        north.text = str(lat_max)
        south = SubElement(latlonbox, "south")
        south.text = str(lat_min)
        east = SubElement(latlonbox, "east")
        east.text = str(lon_max)
        west = SubElement(latlonbox, "west")
        west.text = str(lon_min)

        # Create PNG
        rgb_png = (rgb_regular * 255).astype(np.uint8)
        rgb_png = np.flipud(rgb_png)

        temp_png = os.path.join(output_dir, png_name)
        fig_temp, ax_temp = plt.subplots(figsize=(10, 10))
        ax_temp.imshow(
            rgb_png, origin="lower", extent=[lon_min, lon_max, lat_min, lat_max]
        )
        ax_temp.axis("off")
        fig_temp.savefig(temp_png, dpi=300, bbox_inches="tight", pad_inches=0)
        plt.close(fig_temp)

        # Create KMZ
        rough_string = tostring(kml, "utf-8")
        reparsed = minidom.parseString(rough_string)
        kml_content = reparsed.toprettyxml(indent="  ")

        with zipfile.ZipFile(kmz_file, "w") as kmz:
            kmz.writestr("doc.kml", kml_content)
            kmz.write(temp_png, png_name)

        os.remove(temp_png)
        print(f"    KMZ saved to: {kmz_file}")

    except Exception as e:
        print(f"    Warning: KMZ export failed: {e}")


def create_animated_gif(
    output_dir, base_filename, variable, gif_sequence, duration=0.8
):
    """Create animated GIF from GeoTIFF sequence"""
    try:
        from PIL import Image
        import numpy as np
        import rasterio

        print(f"Creating animated GIF from {len(gif_sequence)} GeoTIFF files...")

        gif_frames = []

        for combo_name in gif_sequence:
            # Look for GeoTIFF file in the combination subdirectory
            combo_dir = os.path.join(output_dir, combo_name)

            # Find the GeoTIFF file (assumes single file per combination)
            geotiff_files = [f for f in os.listdir(combo_dir) if f.endswith(".tif")]

            if not geotiff_files:
                print(
                    f"Warning: No GeoTIFF found for combination {combo_name}, skipping..."
                )
                continue

            geotiff_path = os.path.join(combo_dir, geotiff_files[0])

            # Read GeoTIFF and convert to RGBA for GIF (preserving transparency)
            with rasterio.open(geotiff_path) as src:
                # Read RGBA bands (bands 1, 2, 3, 4)
                if src.count >= 4:
                    # Read all 4 bands including alpha
                    rgba_data = np.stack(
                        [
                            src.read(1),  # Red
                            src.read(2),  # Green
                            src.read(3),  # Blue
                            src.read(4),  # Alpha
                        ],
                        axis=2,
                    )

                    # Convert to PIL Image with transparency
                    rgba_img = Image.fromarray(rgba_data, mode="RGBA")
                else:
                    # Fallback to RGB if no alpha channel
                    rgb_data = np.stack(
                        [src.read(1), src.read(2), src.read(3)],  # Red  # Green  # Blue
                        axis=2,
                    )

                    # Convert to RGBA with full opacity
                    rgba_img = Image.fromarray(rgb_data, mode="RGB").convert("RGBA")

                # Add text label with combination name
                from PIL import ImageDraw, ImageFont

                draw = ImageDraw.Draw(rgba_img)

                # Try to use default font, fallback if not available
                try:
                    font = ImageFont.truetype("arial.ttf", 40)
                except:
                    font = ImageFont.load_default()

                # Add label in top-left corner with semi-transparent background
                text = f"{combo_name.upper()}"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # Draw background rectangle with transparency
                draw.rectangle(
                    [10, 10, 20 + text_width, 20 + text_height], fill=(0, 0, 0, 180)
                )
                # Draw text
                draw.text((15, 15), text, fill=(255, 255, 255, 255), font=font)

                gif_frames.append(rgba_img)
                print(f"  Added frame: {combo_name}")

        if not gif_frames:
            print("Error: No valid frames found for GIF creation")
            return None

        # Create animated GIF with transparency
        gif_filename = os.path.join(
            output_dir, f"{base_filename}_L1B_RGB_{variable}_animated.gif"
        )

        # Convert RGBA frames to indexed color with transparency for GIF format
        gif_frames_indexed = []
        transparency_index = 255  # Reserve index 255 for transparency

        for frame in gif_frames:
            # Convert RGBA to P (palette) mode with transparency
            # First convert to RGB with white background for better palette generation
            rgb_background = Image.new("RGB", frame.size, (255, 255, 255))
            rgb_background.paste(frame, mask=frame.split()[3])  # Use alpha as mask

            # Convert to palette mode with maximum 255 colors (reserve 1 for transparency)
            indexed_frame = rgb_background.quantize(colors=255, method=Image.MEDIANCUT)

            # Extract alpha channel and apply as transparency
            alpha = frame.split()[3]

            # Create transparency mask
            transparency_mask = (
                np.array(alpha) == 0
            )  # Only fully transparent pixels (alpha = 0)

            if transparency_mask.any():
                # Convert to array and reserve index 255 for transparency
                indexed_array = np.array(indexed_frame)

                # Set transparent pixels to reserved index 255
                indexed_array[transparency_mask] = transparency_index
                indexed_frame = Image.fromarray(indexed_array, mode="P")

                print(f"    Transparent pixels: {np.sum(transparency_mask)}")

            gif_frames_indexed.append(indexed_frame)

        # Save animated GIF with transparency
        gif_frames_indexed[0].save(
            gif_filename,
            save_all=True,
            append_images=gif_frames_indexed[1:],
            duration=int(duration * 1000),  # Convert to milliseconds
            loop=0,  # Infinite loop
            transparency=transparency_index,  # Make reserved index transparent
            disposal=2,  # Clear frame before next (important for transparency)
        )

        print(f"Animated GIF saved to: {gif_filename}")
        return gif_filename

    except ImportError:
        print("Warning: PIL (Pillow) not available, cannot create animated GIF")
        return None
    except Exception as e:
        print(f"Warning: GIF creation failed: {e}")
        return None


def generate_rgb_batch(
    filenames,
    output_base=None,
    combinations=None,
    variable="i",
    norm_factor=300,
    formats=None,
    fixed_grid=False,
    grid_resolution=0.03,
    grid_extent=None,
    create_gif=False,
):
    """
    Generate multiple RGB combinations for one or more L1B files (with stitching)

    Args:
        filenames (str or list): Path to L1B file(s) - if list, files will be stitched in order
        output_base (str): Base output directory
        combinations (list): List of combination names to generate
        variable (str): Variable to plot
        norm_factor (int): Normalization factor
        formats (list): Output formats to generate
        fixed_grid (bool): Use fixed regular grid instead of native grid
        grid_resolution (float): Grid resolution in degrees (default: 0.03)
        grid_extent (list): Grid extent as [lat_min, lat_max, lon_min, lon_max] or 'global' for full Earth
        create_gif (bool): Create animated GIF from GeoTIFF sequence (requires geotiff format)

    Returns:
        dict: Results summary
    """
    # Convert single filename to list
    if isinstance(filenames, str):
        filenames = [filenames]

    # Validate input files
    for filename in filenames:
        validate_file(filename)

    print(f"Processing {len(filenames)} L1B file(s):")
    for i, f in enumerate(filenames):
        print(f"  {i+1}. {os.path.basename(f)}")

    print(f"Using {len(RGB_COMBINATIONS)} predefined RGB combinations")

    # Set default output directory
    if output_base is None:
        output_base = os.path.dirname(filenames[0])

    # Create output directory - use first filename for naming
    if len(filenames) == 1:
        output_dir = create_output_directory(output_base, filenames[0])
    else:
        # For multiple files, create a stitched directory name
        first_file = os.path.splitext(os.path.basename(filenames[0]))[0]
        last_file = os.path.splitext(os.path.basename(filenames[-1]))[0]
        stitched_name = f"{first_file}_to_{last_file}_stitched"
        output_dir = os.path.join(output_base, f"{stitched_name}_RGB_batch")
        os.makedirs(output_dir, exist_ok=True)

    # Set default combinations
    if combinations is None:
        combinations = list(RGB_COMBINATIONS.keys())

    # Set default formats
    if formats is None:
        formats = ["png"]

    results = {
        "filenames": filenames,
        "output_dir": output_dir,
        "successful": [],
        "failed": [],
        "total_time": 0,
    }

    print(f"Output directory: {output_dir}")
    print(f"Generating {len(combinations)} RGB combinations...")
    print("-" * 60)

    # Read and stitch L1B data if multiple files
    if len(filenames) == 1:
        print("Processing single L1B file...")
        from nasa_pace_data_reader import L1

        l1b = L1.L1B()
        l1b_dict = l1b.read(filenames[0])
        base_filename = os.path.splitext(os.path.basename(filenames[0]))[0]
    else:
        print("Stitching multiple L1B files...")
        l1b_dict = stitch_l1b_data(filenames, variable)
        first_file = os.path.splitext(os.path.basename(filenames[0]))[0]
        last_file = os.path.splitext(os.path.basename(filenames[-1]))[0]
        base_filename = f"{first_file}_to_{last_file}_stitched"

    start_time = time.time()

    for i, combo_name in enumerate(combinations, 1):
        if combo_name not in RGB_COMBINATIONS:
            print(f"Warning: Unknown combination '{combo_name}', skipping...")
            continue

        combo = RGB_COMBINATIONS[combo_name]
        print(f"[{i}/{len(combinations)}] {combo_name}: {combo['description']}")
        print(f"  View angles: {combo['angles']}")

        try:
            # Create subdirectory for this combination
            combo_dir = os.path.join(output_dir, combo_name)
            os.makedirs(combo_dir, exist_ok=True)

            # Generate RGB using stitched data with fixed grid support
            # Create a temporary filename for the create_l1b_rgb function
            temp_filename = f"{base_filename}.nc"  # Placeholder filename

            # Save stitched data temporarily and call create_l1b_rgb
            result = create_l1b_rgb_from_dict(
                l1b_dict=l1b_dict,
                temp_filename=temp_filename,
                output_dir=combo_dir,
                view_angles=combo["angles"],
                norm_factor=norm_factor,
                variable=variable,
                save_fig="png" in formats,
                save_geotiff="geotiff" in formats,
                save_kmz="kmz" in formats,
                fixed_grid=fixed_grid,
                grid_resolution=grid_resolution,
                grid_extent=grid_extent,
            )

            results["successful"].append(
                {
                    "name": combo_name,
                    "angles": combo["angles"],
                    "description": combo["description"],
                    "output_dir": combo_dir,
                }
            )

            print(f"  ✓ Success - Shape: {result['metadata']['shape']}")

        except Exception as e:
            print(f"  ✗ Failed: {str(e)}")
            results["failed"].append({"name": combo_name, "error": str(e)})

    results["total_time"] = time.time() - start_time

    # Create animated GIF if requested and geotiff format was used
    if create_gif and "geotiff" in formats and len(results["successful"]) > 1:
        print("\n" + "-" * 60)
        print("Creating animated GIF...")

        # Define the viewing angle sequence for GIF
        gif_sequence = ["p55", "p44", "p34", "p20", "n20", "n33", "n44", "n55"]

        # Filter to only include successfully generated combinations
        successful_names = [combo["name"] for combo in results["successful"]]
        available_sequence = [name for name in gif_sequence if name in successful_names]

        if len(available_sequence) >= 2:
            gif_file = create_animated_gif(
                output_dir, base_filename, variable, available_sequence
            )
            if gif_file:
                results["gif_file"] = gif_file
            print(f"GIF sequence: {' -> '.join(available_sequence)}")
        else:
            print(
                "Warning: Need at least 2 combinations from the sequence for GIF creation"
            )
            print(f"Available: {successful_names}")
            print(f"Required sequence: {gif_sequence}")
    elif create_gif and "geotiff" not in formats:
        print("Warning: GIF creation requires 'geotiff' format to be enabled")

    print("\n" + "-" * 60)
    print(f"Batch processing complete!")
    print(f"Successful: {len(results['successful'])}")
    print(f"Failed: {len(results['failed'])}")
    print(f"Total time: {results['total_time']:.1f} seconds")
    if create_gif and "gif_file" in results:
        print(f"Animated GIF: {os.path.basename(results['gif_file'])}")

    # Create summary file
    summary_file = os.path.join(output_dir, "batch_summary.txt")
    with open(summary_file, "w") as f:
        f.write(f"RGB Batch Processing Summary\n")
        f.write(f"{'='*50}\n")
        f.write(f"Input files: {[os.path.basename(f) for f in filenames]}\n")
        f.write(f"Variable: {variable}\n")
        f.write(f"Normalization factor: {norm_factor}\n")
        f.write(f"Output formats: {', '.join(formats)}\n")
        f.write(f"Processing time: {results['total_time']:.1f} seconds\n\n")

        f.write(f"Successful combinations ({len(results['successful'])}):\n")
        for combo in results["successful"]:
            f.write(f"  - {combo['name']}: {combo['description']} {combo['angles']}\n")

        if results["failed"]:
            f.write(f"\nFailed combinations ({len(results['failed'])}):\n")
            for combo in results["failed"]:
                f.write(f"  - {combo['name']}: {combo['error']}\n")

    print(f"Summary saved to: {summary_file}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate multiple RGB combinations from PACE HARP2 L1B data",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Required arguments
    parser.add_argument(
        "--files",
        "-f",
        type=str,
        nargs="+",
        required=True,
        help="Path(s) to L1B file(s). Multiple files will be stitched in order.",
    )

    # Optional arguments
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Base output directory (default: same as input file)",
    )

    parser.add_argument(
        "--variable",
        "-v",
        type=str,
        default="i",
        choices=["i", "q", "u", "dolp"],
        help="Variable to plot (default: i)",
    )

    parser.add_argument(
        "--norm-factor",
        type=int,
        default=300,
        help="Normalization factor (default: 300)",
    )

    parser.add_argument(
        "--combinations",
        "-c",
        type=str,
        nargs="+",
        choices=list(RGB_COMBINATIONS.keys()) + ["all"],
        default="all",
        help=f"RGB combinations to generate. Available: {list(RGB_COMBINATIONS.keys())}",
    )

    parser.add_argument(
        "--formats",
        type=str,
        nargs="+",
        choices=["png", "geotiff", "kmz"],
        default=["png"],
        help="Output formats to generate (default: png)",
    )

    parser.add_argument(
        "--list-combinations",
        action="store_true",
        help="List all available RGB combinations and exit",
    )

    parser.add_argument(
        "--fixed-grid",
        action="store_true",
        help="Use fixed regular grid instead of native lat-lon grid",
    )

    parser.add_argument(
        "--grid-resolution",
        type=float,
        default=0.03,
        help="Grid resolution in degrees (default: 0.03)",
    )

    parser.add_argument(
        "--grid-extent",
        type=str,
        default="global",
        help="Grid extent: 'global' for full Earth or 'lat_min,lat_max,lon_min,lon_max' (default: global)",
    )

    parser.add_argument(
        "--create-gif",
        action="store_true",
        help="Create animated GIF from GeoTIFF sequence (requires --formats geotiff). Sequence: p55→p44→p34→p20→n20→n33→n44→n55",
    )

    args = parser.parse_args()

    # List combinations if requested
    if args.list_combinations:
        print("Available RGB combinations:")
        print("=" * 50)
        for name, combo in RGB_COMBINATIONS.items():
            print(f"{name:12} {str(combo['angles']):15} - {combo['description']}")
        return

    # Validate input files
    for filename in args.files:
        if not os.path.exists(filename):
            print(f"Error: File {filename} does not exist")
            sys.exit(1)

    # Set combinations
    combinations = (
        list(RGB_COMBINATIONS.keys())
        if "all" in args.combinations
        else args.combinations
    )

    # Parse grid extent
    grid_extent = "global"  # Default
    if args.grid_extent:
        if args.grid_extent.lower() == "global":
            grid_extent = "global"
        else:
            try:
                extent_vals = [float(x.strip()) for x in args.grid_extent.split(",")]
                if len(extent_vals) == 4:
                    grid_extent = extent_vals
                else:
                    print(
                        "Error: Grid extent must have 4 values: lat_min,lat_max,lon_min,lon_max"
                    )
                    sys.exit(1)
            except ValueError:
                print("Error: Invalid grid extent values")
                sys.exit(1)

    # Generate RGB batch
    try:
        results = generate_rgb_batch(
            filenames=args.files,
            output_base=args.output,
            combinations=combinations,
            variable=args.variable,
            norm_factor=args.norm_factor,
            formats=args.formats,
            fixed_grid=args.fixed_grid,
            grid_resolution=args.grid_resolution,
            grid_extent=grid_extent,
            create_gif=args.create_gif,
        )

        if results["failed"]:
            print(f"\nWarning: {len(results['failed'])} combinations failed")
            sys.exit(1)
        else:
            print("\nAll combinations generated successfully!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
