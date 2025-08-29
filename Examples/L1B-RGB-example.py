#!/usr/bin/env python
"""
L1B RGB Image Generation Script

This script demonstrates how to create RGB images from NASA PACE HARP2 L1B data.
It reads L1B data and generates RGB images using different viewing angles and wavelengths.

Created by Anin Puthukkudy (ESI, UMBC)
"""

from nasa_pace_data_reader import L1, plot
from matplotlib import pyplot as plt
import numpy as np
import argparse
import os
from pathlib import Path

# suppress warnings
import warnings

warnings.filterwarnings("ignore")


def create_l1b_rgb(
    filename,
    output_dir=None,
    view_angles=None,
    norm_factor=300,
    variable="i",
    save_fig=True,
    show_plot=False,
    save_geotiff=False,
    save_kmz=False,
    fixed_grid=False,
    grid_resolution=0.03,
    grid_extent=None,
):
    """
    Create RGB images from L1B data

    Args:
        filename (str): Path to the L1B file
        output_dir (str): Directory to save the images (optional)
        view_angles (list): List of 3 view angle indices for RGB [R, G, B]
        norm_factor (int): Normalization factor for the RGB plot
        variable (str): Variable to plot ("i", "dolp", etc.)
        save_fig (bool): Whether to save the figure
        show_plot (bool): Whether to display the plot
        save_geotiff (bool): Whether to save as GeoTIFF
        save_kmz (bool): Whether to save as KMZ
        fixed_grid (bool): Use fixed regular grid instead of native grid
        grid_resolution (float): Grid resolution in degrees (default: 0.03)
        grid_extent (list): Grid extent as [lat_min, lat_max, lon_min, lon_max] or 'global' for full Earth

    Returns:
        dict: Dictionary containing RGB data and metadata
    """

    # Default view angles if not specified
    if view_angles is None:
        view_angles = [36, 4, 84]  # Default red, green, blue indices

    # Read the L1B file
    print(f"Reading L1B data from: {filename}")
    l1b = L1.L1B()
    l1b_dict = l1b.read(filename)

    # Create RGB manually for L1B data (3D: angle, y, x)
    print(
        f"Generating RGB image using variable '{variable}' at view angles {view_angles}"
    )

    # Get data dimensions
    data_shape = l1b_dict[variable].shape
    print(f"Data shape: {data_shape}")

    # Get lat-lon grids for each channel (use float32 for processing speed)
    lat_r = l1b_dict["latitude"][view_angles[0], :, :].astype(np.float32)
    lat_g = l1b_dict["latitude"][view_angles[1], :, :].astype(np.float32)
    lat_b = l1b_dict["latitude"][view_angles[2], :, :].astype(np.float32)

    lon_r = l1b_dict["longitude"][view_angles[0], :, :].astype(np.float32)
    lon_g = l1b_dict["longitude"][view_angles[1], :, :].astype(np.float32)
    lon_b = l1b_dict["longitude"][view_angles[2], :, :].astype(np.float32)

    if fixed_grid:
        print(f"Using fixed regular grid with {grid_resolution}° resolution")

        # Determine grid bounds - default to global if not specified
        if grid_extent == "global" or grid_extent is None:
            # Full Earth coverage
            lat_min, lat_max = -90.0, 90.0
            lon_min, lon_max = -180.0, 180.0
            print("Using global grid extent: lat [-90, 90], lon [-180, 180]")
        elif grid_extent is not None and len(grid_extent) == 4:
            # Custom extent: [lat_min, lat_max, lon_min, lon_max]
            lat_min, lat_max, lon_min, lon_max = grid_extent
            print(
                f"Using custom grid extent: lat [{lat_min}, {lat_max}], lon [{lon_min}, {lon_max}]"
            )
        else:
            print(
                "Error: Invalid grid extent specified, use 'global' or provide lat_min,lat_max,lon_min,lon_max"
            )
            raise ValueError("Invalid grid extent for fixed grid")

        # Create regular grid with specified resolution
        lat_grid_1d = np.arange(
            lat_min, lat_max + grid_resolution / 2, grid_resolution, dtype=np.float32
        )
        lon_grid_1d = np.arange(
            lon_min, lon_max + grid_resolution / 2, grid_resolution, dtype=np.float32
        )

        # Create 2D grids
        ref_lon, ref_lat = np.meshgrid(lon_grid_1d, lat_grid_1d)

        print(f"Fixed grid shape: {ref_lat.shape}")
        print(
            f"Grid resolution: {grid_resolution}° ({grid_resolution*111:.1f}km at equator)"
        )
        print(
            f"Grid bounds: lat [{lat_min:.3f}, {lat_max:.3f}], lon [{lon_min:.3f}, {lon_max:.3f}]"
        )
    else:
        # Use red channel as reference grid (original behavior)
        ref_lat = lat_r
        ref_lon = lon_r

    ref_shape = ref_lat.shape

    # Extract data for each channel (keep as float32 for sensor data precision)
    red_data = l1b_dict[variable][view_angles[0], :, :].astype(np.float32)
    green_data = l1b_dict[variable][view_angles[1], :, :].astype(np.float32)
    blue_data = l1b_dict[variable][view_angles[2], :, :].astype(np.float32)

    # Create RGB array with reference grid shape
    rgb_data = np.zeros((ref_shape[0], ref_shape[1], 3), dtype=np.float32)

    # Use pyresample for regridding channels to reference grid
    from pyresample import geometry, kd_tree

    # Define target geometry (reference grid)
    target_def = geometry.SwathDefinition(lons=ref_lon, lats=ref_lat)

    if fixed_grid:
        # For fixed grid, regrid all channels including red

        # Red channel
        red_def = geometry.SwathDefinition(lons=lon_r, lats=lat_r)
        try:
            red_regridded = kd_tree.resample_nearest(
                red_def,
                red_data,
                target_def,
                radius_of_influence=5000,  # 5km radius
                fill_value=0,
                nprocs=1,
            )
            valid_red = ~np.isnan(red_regridded)
            rgb_data[:, :, 0] = np.where(valid_red, red_regridded, 0)
            del red_regridded, valid_red
        except Exception as e:
            print(f"Warning: Red channel regridding failed: {e}")
            rgb_data[:, :, 0] = 0

        # Create masks for valid data in fixed grid mode
        valid_ref = ~(np.isnan(ref_lat) | np.isnan(ref_lon))
    else:
        # Red channel - no interpolation needed (reference)
        rgb_data[:, :, 0] = red_data
        # Create masks for valid data in native grid mode
        valid_ref = ~(np.isnan(ref_lat) | np.isnan(ref_lon) | np.isnan(red_data))

    valid_green = ~(np.isnan(lat_g) | np.isnan(lon_g) | np.isnan(green_data))
    valid_blue = ~(np.isnan(lat_b) | np.isnan(lon_b) | np.isnan(blue_data))

    # Regrid green channel with better parameters
    green_def = geometry.SwathDefinition(lons=lon_g, lats=lat_g)
    try:
        green_regridded = kd_tree.resample_nearest(
            green_def,
            green_data,
            target_def,
            radius_of_influence=5000,  # 5km radius
            fill_value=-999,
            nprocs=1,  # Single process to avoid issues
        )
        # Only use regridded values where both source and target are valid
        green_mask = ~np.isnan(green_regridded) & valid_ref
        rgb_data[:, :, 1] = np.where(green_mask, green_regridded, 0)
        # Memory cleanup
        del green_regridded, green_mask
    except Exception as e:
        print(f"Warning: Green channel regridding failed: {e}")
        rgb_data[:, :, 1] = 0

    # Clean up green channel data
    del lat_g, lon_g, green_data, valid_green

    # Regrid blue channel with better parameters
    blue_def = geometry.SwathDefinition(lons=lon_b, lats=lat_b)
    try:
        blue_regridded = kd_tree.resample_nearest(
            blue_def,
            blue_data,
            target_def,
            radius_of_influence=5000,  # 5km radius
            fill_value=-999,
            nprocs=1,  # Single process to avoid issues
        )
        # Only use regridded values where both source and target are valid
        blue_mask = ~np.isnan(blue_regridded) & valid_ref
        rgb_data[:, :, 2] = np.where(blue_mask, blue_regridded, 0)
        # Memory cleanup
        del blue_regridded, blue_mask
    except Exception as e:
        print(f"Warning: Blue channel regridding failed: {e}")
        rgb_data[:, :, 2] = 0

    # Clean up blue channel data
    del lat_b, lon_b, blue_data, valid_blue

    # Normalize the RGB data
    if norm_factor > 0:
        rgb_data = rgb_data / norm_factor
        # Clip values to [0, 1] range
        rgb_data = np.clip(rgb_data, 0, 1)
    else:
        # Auto-normalize using percentiles
        for i in range(3):
            channel = rgb_data[:, :, i]
            valid_data = channel[~np.isnan(channel)]
            if len(valid_data) > 0:
                vmin = np.percentile(valid_data, 5)
                vmax = np.percentile(valid_data, 95)
                rgb_data[:, :, i] = (channel - vmin) / (vmax - vmin)
                rgb_data[:, :, i] = np.clip(rgb_data[:, :, i], 0, 1)

    # Handle NaN values
    rgb_data = np.nan_to_num(rgb_data, nan=0.0)

    # Save GeoTIFF if requested
    if save_geotiff and output_dir:
        try:
            import rasterio
            from rasterio.warp import calculate_default_transform, reproject, Resampling
            from rasterio.crs import CRS
            import tempfile

            os.makedirs(output_dir, exist_ok=True)
            base_filename = os.path.splitext(os.path.basename(filename))[0]
            geotiff_file = os.path.join(
                output_dir,
                f"{base_filename}_L1B_RGB_{variable}_angles_{view_angles[0]}_{view_angles[1]}_{view_angles[2]}.tif",
            )

            # Use pyresample to create a regular grid for GeoTIFF
            from pyresample import geometry, kd_tree

            # Get data bounds
            lat_min, lat_max = np.nanmin(ref_lat), np.nanmax(ref_lat)
            lon_min, lon_max = np.nanmin(ref_lon), np.nanmax(ref_lon)

            # Create a regular grid with appropriate resolution
            # Use roughly the same number of pixels but in regular grid
            grid_size = min(ref_lat.shape)  # Use smaller dimension for square grid

            # Create regular lat/lon grid (use float32 for processing speed)
            lats_reg = np.linspace(lat_min, lat_max, grid_size, dtype=np.float32)
            lons_reg = np.linspace(lon_min, lon_max, grid_size, dtype=np.float32)
            lon_grid_reg, lat_grid_reg = np.meshgrid(lons_reg, lats_reg)

            # Define source and target geometries
            source_def = geometry.SwathDefinition(lons=ref_lon, lats=ref_lat)
            target_def = geometry.GridDefinition(lons=lon_grid_reg, lats=lat_grid_reg)

            # Check for missing data in original RGB data before resampling
            valid_data_mask = np.ones(rgb_data.shape[:2], dtype=bool)
            for i in range(3):
                channel_valid = ~(
                    np.isnan(rgb_data[:, :, i]) | (rgb_data[:, :, i] == 0)
                )
                valid_data_mask = valid_data_mask & channel_valid

            # Resample RGB data to regular grid using NaN as fill value
            rgb_regular = np.full((grid_size, grid_size, 3), np.nan, dtype=np.float32)
            valid_regular = np.zeros((grid_size, grid_size), dtype=bool)

            # First resample the validity mask
            valid_regular_result = kd_tree.resample_nearest(
                source_def,
                valid_data_mask.astype(float),
                target_def,
                radius_of_influence=10000,  # 10km
                fill_value=0,
            )
            valid_regular = (
                np.array(valid_regular_result) > 0.5
            )  # Convert back to boolean

            # Then resample each RGB channel, but only where we have valid data
            for i in range(3):
                # Create masked data where invalid pixels are NaN
                masked_data = rgb_data[:, :, i].copy()
                masked_data[~valid_data_mask] = np.nan

                rgb_regular[:, :, i] = kd_tree.resample_nearest(
                    source_def,
                    masked_data,
                    target_def,
                    radius_of_influence=10000,  # 10km
                    fill_value=-999,
                )

            # Create alpha channel for transparency
            alpha_channel = np.ones((grid_size, grid_size), dtype=np.uint8) * 255

            # Make areas transparent where:
            # 1. No valid data was resampled to this location
            # 2. Any RGB channel is NaN or zero after resampling
            missing_data_mask = (
                ~valid_regular  # No valid source data
                | np.any(np.isnan(rgb_regular), axis=2)  # Any channel has NaN
                | np.any(rgb_regular <= 0, axis=2)  # Any channel is zero or negative
            )
            alpha_channel[missing_data_mask] = 0

            # Replace NaN values with 0 for the RGB channels (but keep alpha transparency)
            rgb_regular = np.nan_to_num(rgb_regular, nan=0.0)

            # Convert RGB to uint8
            rgb_uint8 = (rgb_regular * 255).astype(np.uint8)

            # Calculate proper transform for regular grid
            pixel_width = (lon_max - lon_min) / grid_size
            pixel_height = (lat_max - lat_min) / grid_size

            # Create transform (note: rasterio uses top-left origin)
            from rasterio.transform import from_bounds

            transform_matrix = from_bounds(
                lon_min, lat_min, lon_max, lat_max, grid_size, grid_size
            )

            # Write GeoTIFF with RGBA (including alpha for transparency)
            with rasterio.open(
                geotiff_file,
                "w",
                driver="GTiff",
                height=grid_size,
                width=grid_size,
                count=4,  # RGBA
                dtype=rgb_uint8.dtype,
                crs=CRS.from_epsg(4326),  # WGS84
                transform=transform_matrix,
                compress="lzw",
            ) as dst:
                # Write RGB bands (rasterio expects row order from top to bottom)
                for i in range(3):
                    dst.write(np.flipud(rgb_uint8[:, :, i]), i + 1)
                # Write alpha band
                dst.write(np.flipud(alpha_channel), 4)

            print(f"GeoTIFF saved to: {geotiff_file}")

        except ImportError:
            print("Warning: rasterio not available, skipping GeoTIFF export")
        except Exception as e:
            print(f"Warning: GeoTIFF export failed: {e}")

    # Save KMZ if requested
    if save_kmz and output_dir:
        try:
            import zipfile
            from xml.etree.ElementTree import Element, SubElement, tostring
            from xml.dom import minidom
            from pyresample import geometry, kd_tree

            os.makedirs(output_dir, exist_ok=True)
            base_filename = os.path.splitext(os.path.basename(filename))[0]
            kmz_file = os.path.join(
                output_dir,
                f"{base_filename}_L1B_RGB_{variable}_angles_{view_angles[0]}_{view_angles[1]}_{view_angles[2]}.kmz",
            )
            png_name = f"L1B_RGB_{variable}.png"

            # Get data bounds
            lat_min, lat_max = np.nanmin(ref_lat), np.nanmax(ref_lat)
            lon_min, lon_max = np.nanmin(ref_lon), np.nanmax(ref_lon)

            # Create a regular grid for proper KMZ alignment
            grid_size = min(ref_lat.shape)  # Use smaller dimension for square grid

            # Create regular lat/lon grid (use float32 for processing speed)
            lats_reg = np.linspace(lat_min, lat_max, grid_size, dtype=np.float32)
            lons_reg = np.linspace(lon_min, lon_max, grid_size, dtype=np.float32)
            lon_grid_reg, lat_grid_reg = np.meshgrid(lons_reg, lats_reg)

            # Define source and target geometries
            source_def = geometry.SwathDefinition(lons=ref_lon, lats=ref_lat)
            target_def = geometry.GridDefinition(lons=lon_grid_reg, lats=lat_grid_reg)

            # Resample RGB data to regular grid
            rgb_regular = np.zeros((grid_size, grid_size, 3), dtype=np.float32)
            for i in range(3):
                rgb_regular[:, :, i] = kd_tree.resample_nearest(
                    source_def,
                    rgb_data[:, :, i],
                    target_def,
                    radius_of_influence=10000,  # 10km
                    fill_value=0,
                )

            # Create KML content
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

            # Pretty print XML
            rough_string = tostring(kml, "utf-8")
            reparsed = minidom.parseString(rough_string)
            kml_content = reparsed.toprettyxml(indent="  ")

            # Convert RGB to PNG format for KMZ (flip for proper orientation)
            rgb_png = (rgb_regular * 255).astype(np.uint8)
            rgb_png = np.flipud(rgb_png)  # Flip for Google Earth orientation

            # Save PNG temporarily with proper aspect ratio
            temp_png = os.path.join(output_dir, png_name)
            fig_temp, ax_temp = plt.subplots(figsize=(10, 10))  # Square aspect ratio
            ax_temp.imshow(
                rgb_png, origin="lower", extent=[lon_min, lon_max, lat_min, lat_max]
            )
            ax_temp.axis("off")
            fig_temp.savefig(temp_png, dpi=300, bbox_inches="tight", pad_inches=0)
            plt.close(fig_temp)

            # Create KMZ file
            with zipfile.ZipFile(kmz_file, "w") as kmz:
                kmz.writestr("doc.kml", kml_content)
                kmz.write(temp_png, png_name)

            # Clean up temp PNG
            os.remove(temp_png)

            print(f"KMZ saved to: {kmz_file}")

        except Exception as e:
            print(f"Warning: KMZ export failed: {e}")

    # Display or save the image
    if show_plot or save_fig:
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.imshow(rgb_data, origin="lower")
        ax.set_title(f"L1B RGB Image - {variable.upper()}\nView Angles: {view_angles}")
        ax.set_xlabel("X Pixel")
        ax.set_ylabel("Y Pixel")

        if save_fig and output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_filename = os.path.splitext(os.path.basename(filename))[0]
            output_file = os.path.join(
                output_dir,
                f"{base_filename}_L1B_RGB_{variable}_angles_{view_angles[0]}_{view_angles[1]}_{view_angles[2]}.png",
            )
            fig.savefig(output_file, dpi=300, bbox_inches="tight")
            print(f"RGB image saved to: {output_file}")

        if show_plot:
            plt.show()
        else:
            plt.close(fig)

    # Return results
    return {
        "rgb_data": rgb_data,
        "view_angles": view_angles,
        "variable": variable,
        "wavelengths": [l1b_dict["intensity_wavelength"][i] for i in view_angles],
        "viewing_angles": [l1b_dict["view_angles"][i] for i in view_angles],
        "metadata": {
            "date_time": l1b_dict.get("date_time", "Unknown"),
            "shape": rgb_data.shape if rgb_data is not None else None,
        },
    }


def create_projected_rgb(
    filename,
    output_dir=None,
    view_angles=None,
    norm_factor=300,
    variable="i",
    projection="PlateCarree",
    save_fig=True,
):
    """
    Create projected RGB images from L1B data using single view angle

    Args:
        filename (str): Path to the L1B file
        output_dir (str): Directory to save the images
        view_angles (list): List of 3 view angle indices for RGB (only first one used for L1B)
        norm_factor (int): Normalization factor
        variable (str): Variable to plot
        projection (str): Map projection type
        save_fig (bool): Whether to save the figure

    Returns:
        str: Path to saved image
    """

    if view_angles is None:
        view_angles = [36, 4, 84]

    # Read the L1B file
    print(f"Creating projected RGB from: {filename}")
    l1b = L1.L1B()
    l1b_dict = l1b.read(filename)

    # Create the plot object
    plt_ = plot.Plot(l1b_dict)

    # For L1B, use projectVar method which handles single view angles properly
    # Use the first view angle from the list
    view_angle_deg = l1b_dict["view_angles"][view_angles[0]]

    print(f"Projecting variable '{variable}' at view angle {view_angle_deg} degrees")

    # Set the band for proper wavelength selection
    plt_.setBand("green")  # This sets a default wavelength

    # Project the variable
    try:
        result = plt_.projectVar(
            var=variable,
            viewAngle=view_angle_deg,
            level="L1B",
            saveFig=save_fig,
            savePath=output_dir,
            proj=projection,
            vmax=None if variable != "dolp" else 0.3,
        )
    except Exception as e:
        print(f"Projection '{projection}' failed, trying 'PlateCarree': {e}")
        # Fall back to a basic projection
        result = plt_.projectVar(
            var=variable,
            viewAngle=view_angle_deg,
            level="L1B",
            saveFig=save_fig,
            savePath=output_dir,
            proj="PlateCarree",
            vmax=None if variable != "dolp" else 0.3,
        )

    if save_fig and output_dir:
        # The projectVar method should save the file automatically
        expected_filename = (
            f"{plt_.instrument}_{variable}_{view_angle_deg}_proj_{projection}.png"
        )
        if output_dir:
            expected_path = os.path.join(output_dir, expected_filename)
        else:
            expected_path = f"./{expected_filename}"
        print(f"Projected image should be saved at: {expected_path}")
        return expected_path

    return result


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Generate RGB images from PACE HARP2 L1B data",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Required arguments
    parser.add_argument(
        "--file", "-f", type=str, required=True, help="Path to the L1B file"
    )

    # Optional arguments
    parser.add_argument(
        "--output", "-o", type=str, help="Output directory for saving images"
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
        "--angles",
        type=int,
        nargs=3,
        default=[36, 4, 84],
        help="Three view angle indices for RGB (default: 36 4 84)",
    )

    parser.add_argument(
        "--norm-factor",
        type=int,
        default=300,
        help="Normalization factor (default: 300)",
    )

    parser.add_argument(
        "--projected", action="store_true", help="Create projected RGB image"
    )

    parser.add_argument(
        "--projection",
        type=str,
        default="PlateCarree",
        choices=["PlateCarree", "Orthographic", "none"],
        help="Map projection for projected RGB (default: PlateCarree)",
    )

    parser.add_argument("--show", action="store_true", help="Display the plot")

    parser.add_argument("--geotiff", action="store_true", help="Save as GeoTIFF file")

    parser.add_argument(
        "--kmz", action="store_true", help="Save as KMZ file for Google Earth"
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

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} does not exist")
        exit(1)

    # Set output directory
    if args.output is None:
        args.output = os.path.dirname(args.file)

    print(f"Processing L1B file: {args.file}")
    print(f"Variable: {args.variable}")
    print(f"View angles: {args.angles}")
    print(f"Normalization factor: {args.norm_factor}")

    try:
        if args.projected:
            # Create projected RGB (single view angle for L1B)
            result_path = create_projected_rgb(
                args.file,
                output_dir=args.output,
                view_angles=args.angles,
                norm_factor=args.norm_factor,
                variable=args.variable,
                projection=args.projection,
                save_fig=True,
            )
            print(f"Projected image created: {result_path}")
        else:
            # Create standard RGB
            # Parse grid extent
            grid_extent = "global"  # Default
            if args.grid_extent:
                if args.grid_extent.lower() == "global":
                    grid_extent = "global"
                else:
                    try:
                        extent_vals = [
                            float(x.strip()) for x in args.grid_extent.split(",")
                        ]
                        if len(extent_vals) == 4:
                            grid_extent = extent_vals
                        else:
                            print(
                                "Error: Grid extent must have 4 values: lat_min,lat_max,lon_min,lon_max"
                            )
                            exit(1)
                    except ValueError:
                        print("Error: Invalid grid extent values")
                        exit(1)

            result = create_l1b_rgb(
                args.file,
                output_dir=args.output,
                view_angles=args.angles,
                norm_factor=args.norm_factor,
                variable=args.variable,
                save_fig=True,
                show_plot=args.show,
                save_geotiff=args.geotiff,
                save_kmz=args.kmz,
                fixed_grid=args.fixed_grid,
                grid_resolution=args.grid_resolution,
                grid_extent=grid_extent,
            )

            print(f"RGB image created successfully!")
            print(f"Shape: {result['metadata']['shape']}")
            print(f"Wavelengths (nm): {result['wavelengths']}")
            print(f"Viewing angles (deg): {result['viewing_angles']}")

        if args.show:
            plt.show()

    except Exception as e:
        print(f"Error processing file: {e}")
        exit(1)
