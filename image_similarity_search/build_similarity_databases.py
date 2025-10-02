"""
Utility script to build separate image similarity databases for clothing and jewelry.

This script builds two independent FAISS-based similarity search databases:
1. Clothing database - for fashion items (shirts, pants, shoes, etc.)
2. Jewelry database - for jewelry items (necklaces, rings, earrings, etc.)

Usage:
    python build_similarity_databases.py [--clothing-only | --jewelry-only]

    Without flags: Builds both databases
    --clothing-only: Builds only the clothing database
    --jewelry-only: Builds only the jewelry database
"""

import argparse
import sys
from pathlib import Path

from config import SIMILARITY_SEARCH_CONFIG, logger
from image_similarity_search.similarity_search import ImageSimilaritySearch


def build_clothing_database() -> bool:
    """
    Build the clothing similarity database.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("=" * 60)
        logger.info("Building CLOTHING similarity database")
        logger.info("=" * 60)

        clothing_images_dir = Path(SIMILARITY_SEARCH_CONFIG.clothing_images_path)
        clothing_db_path = Path(SIMILARITY_SEARCH_CONFIG.clothing_db_path)

        # Check if images directory exists
        if not clothing_images_dir.exists():
            logger.error(
                f"Clothing images directory does not exist: {clothing_images_dir}"
            )
            logger.info(
                f"Please create the directory and add clothing images: {clothing_images_dir}"
            )
            return False

        # Check if there are images
        image_files = list(clothing_images_dir.glob("*.[jp][pn]g")) + list(
            clothing_images_dir.glob("*.jpeg")
        )
        if not image_files:
            logger.warning(f"No images found in {clothing_images_dir}")
            logger.info("Please add clothing product images to build the database")
            return False

        logger.info(f"Found {len(image_files)} images in {clothing_images_dir}")

        # Create database directory if it doesn't exist
        clothing_db_path.mkdir(parents=True, exist_ok=True)

        # Initialize and build database
        similarity_search = ImageSimilaritySearch(db_path=clothing_db_path)
        similarity_search.build_database(clothing_images_dir)

        logger.info("✓ Clothing database built successfully!")
        logger.info(f"Database saved to: {clothing_db_path}")
        return True

    except Exception as e:
        logger.error(f"Error building clothing database: {e}", exc_info=True)
        return False


def build_jewelry_database() -> bool:
    """
    Build the jewelry similarity database.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("=" * 60)
        logger.info("Building JEWELRY similarity database")
        logger.info("=" * 60)

        jewelry_images_dir = Path(SIMILARITY_SEARCH_CONFIG.jewelry_images_path)
        jewelry_db_path = Path(SIMILARITY_SEARCH_CONFIG.jewelry_db_path)

        # Check if images directory exists
        if not jewelry_images_dir.exists():
            logger.error(
                f"Jewelry images directory does not exist: {jewelry_images_dir}"
            )
            logger.info(
                f"Please create the directory and add jewelry images: {jewelry_images_dir}"
            )
            return False

        # Check if there are images
        image_files = list(jewelry_images_dir.glob("*.[jp][pn]g")) + list(
            jewelry_images_dir.glob("*.jpeg")
        )
        if not image_files:
            logger.warning(f"No images found in {jewelry_images_dir}")
            logger.info("Please add jewelry product images to build the database")
            return False

        logger.info(f"Found {len(image_files)} images in {jewelry_images_dir}")

        # Create database directory if it doesn't exist
        jewelry_db_path.mkdir(parents=True, exist_ok=True)

        # Initialize and build database
        similarity_search = ImageSimilaritySearch(db_path=jewelry_db_path)
        similarity_search.build_database(jewelry_images_dir)

        logger.info("✓ Jewelry database built successfully!")
        logger.info(f"Database saved to: {jewelry_db_path}")
        return True

    except Exception as e:
        logger.error(f"Error building jewelry database: {e}", exc_info=True)
        return False


def main():
    """Main function to build similarity databases."""
    parser = argparse.ArgumentParser(
        description="Build image similarity databases for clothing and jewelry"
    )
    parser.add_argument(
        "--clothing-only",
        action="store_true",
        help="Build only the clothing database",
    )
    parser.add_argument(
        "--jewelry-only",
        action="store_true",
        help="Build only the jewelry database",
    )

    args = parser.parse_args()

    # Determine which databases to build
    build_clothing = not args.jewelry_only
    build_jewelry = not args.clothing_only

    success = True

    logger.info("Starting database build process...")
    logger.info(f"Clothing database: {SIMILARITY_SEARCH_CONFIG.clothing_db_path}")
    logger.info(f"Jewelry database: {SIMILARITY_SEARCH_CONFIG.jewelry_db_path}")
    logger.info("")

    # Build clothing database
    if build_clothing:
        if not build_clothing_database():
            success = False
        logger.info("")

    # Build jewelry database
    if build_jewelry:
        if not build_jewelry_database():
            success = False
        logger.info("")

    # Final summary
    logger.info("=" * 60)
    if success:
        logger.info("✓ All databases built successfully!")
    else:
        logger.warning("⚠ Some databases failed to build. Check logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
