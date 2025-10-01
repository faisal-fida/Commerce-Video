"""
A module for building and searching an image similarity database using CLIP embeddings and FAISS.
"""

import logging
import os
import pickle
from pathlib import Path
from typing import List, Union, Optional

import faiss  # type: ignore
import numpy as np
from PIL import Image
import torch
from transformers import CLIPModel, CLIPProcessor  # type: ignore


# --- Setup Logging ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels

# Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create formatter and add it to the handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

# Add the handler to the logger if not already added
if not logger.handlers:
    logger.addHandler(ch)


class ImageSimilaritySearch:
    """
    A class to build and search an image similarity database using CLIP embeddings.
    """

    EMBEDDINGS_FILE = "image_embeddings.pkl"
    INDEX_FILE = "faiss_index.idx"
    PATHS_FILE = "image_paths.pkl"

    def __init__(
        self,
        db_path: Union[str, Path],
        model_name: str = "openai/clip-vit-base-patch16",
    ):
        """
        Initializes the ImageSimilaritySearch instance.

        Args:
            db_path (Union[str, Path]): Path to the directory where the database files will be stored.
            model_name (str): Name of the Hugging Face model to use for embeddings (default CLIP).
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)  # Create DB directory if it doesn't exist

        self.model_name = model_name
        self.model: Optional[CLIPModel] = None
        self.processor: Optional[CLIPProcessor] = None
        self.index: Optional[faiss.Index] = None
        self.image_paths: List[Path] = []

        logger.info(
            f"Initialized ImageSimilaritySearch with database path: {self.db_path}"
        )

    def _load_model(self):
        """Loads the CLIP model and processor if not already loaded."""
        if self.model is None or self.processor is None:
            logger.info(f"Loading model and processor: {self.model_name}")
            try:
                self.model = CLIPModel.from_pretrained(self.model_name)
                self.processor = CLIPProcessor.from_pretrained(self.model_name)
                logger.info("Model and processor loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load model '{self.model_name}': {e}")
                raise e

    def _embed_image(self, image_path: Path) -> np.ndarray:
        """
        Generates an embedding for a single image.

        Args:
            image_path (Path): Path to the image file.

        Returns:
            np.ndarray: The normalized embedding vector for the image.
        """
        self._load_model()
        try:
            image = Image.open(image_path).convert("RGB")  # Ensure RGB format
            inputs = self.processor(images=image, return_tensors="pt")

            # Use model.get_image_features if available, otherwise use the full model
            # CLIP models typically have this method.
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
            # Normalize the embedding
            image_features = image_features / image_features.norm(
                p=2, dim=-1, keepdim=True
            )
            return image_features.cpu().numpy().flatten()
        except Exception as e:
            logger.error(f"Failed to embed image {image_path}: {e}")
            raise e

    def _embed_text(self, text: str) -> np.ndarray:
        """
        Generates an embedding for a text query.

        Args:
            text (str): The text query.

        Returns:
            np.ndarray: The normalized embedding vector for the text.
        """
        self._load_model()
        try:
            inputs = self.processor(
                text=[text], return_tensors="pt", padding=True, truncation=True
            )

            # Use model.get_text_features if available
            with torch.no_grad():
                text_features = self.model.get_text_features(**inputs)
            # Normalize the embedding
            text_features = text_features / text_features.norm(
                p=2, dim=-1, keepdim=True
            )
            return text_features.cpu().numpy().flatten()
        except Exception as e:
            logger.error(f"Failed to embed text '{text}': {e}")
            raise e

    def build_database(self, images_directory: Union[str, Path]):
        """
        Loads images from a directory, computes their embeddings, and saves them
        along with a FAISS index for efficient similarity search.

        Args:
            images_directory (Union[str, Path]): Path to the directory containing images.
        """
        images_dir = Path(images_directory)
        if not images_dir.exists() or not images_dir.is_dir():
            logger.error(
                f"Images directory does not exist or is not a directory: {images_dir}"
            )
            raise ValueError(f"Invalid images directory: {images_dir}")

        image_paths = [
            p
            for p in images_dir.rglob("*")
            if p.is_file()
            and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
        ]
        if not image_paths:
            logger.warning(f"No images found in directory: {images_dir}")
            return

        logger.info(
            f"Found {len(image_paths)} images in {images_dir}. Computing embeddings..."
        )

        embeddings = []
        valid_image_paths = []
        for img_path in image_paths:
            try:
                embedding = self._embed_image(img_path)
                embeddings.append(embedding)
                valid_image_paths.append(img_path)
                logger.debug(f"Embedded image: {img_path}")
            except Exception as e:
                logger.warning(
                    f"Skipping image due to embedding error: {img_path} - {e}"
                )

        if not embeddings:
            logger.error("No images could be embedded. Database build failed.")
            return

        # Convert embeddings list to a numpy array (num_images, embedding_dim)
        embeddings_array = np.array(embeddings).astype("float32")
        logger.info(f"Computed embeddings for {len(embeddings_array)} images.")

        # Build FAISS index
        dimension = embeddings_array.shape[1]
        # Using IndexFlatIP (Inner Product) for normalized vectors (cosine similarity)
        # For L2 distance, use IndexFlatL2(dimension)
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings_array)
        logger.info("FAISS index built successfully.")

        # Save index and paths
        index_path = self.db_path / self.INDEX_FILE
        paths_path = self.db_path / self.PATHS_FILE
        # embeddings_path = self.db_path / self.EMBEDDINGS_FILE

        faiss.write_index(self.index, str(index_path))
        logger.info(f"FAISS index saved to {index_path}")

        with open(paths_path, "wb") as f:
            pickle.dump(valid_image_paths, f)
        logger.info(f"Image paths saved to {paths_path}")

        # Saving raw embeddings is optional, can be useful for debugging or other tasks
        # but not strictly necessary for search if the index is sufficient.
        # with open(embeddings_path, 'wb') as f:
        #     pickle.dump(embeddings_array, f)
        # logger.info(f"Raw embeddings saved to {embeddings_path}")

        self.image_paths = valid_image_paths  # Update internal state
        logger.info("Database build completed successfully.")

    def _load_database(self):
        """Loads the FAISS index and image paths from the database directory."""
        index_path = self.db_path / self.INDEX_FILE
        paths_path = self.db_path / self.PATHS_FILE

        if not index_path.exists() or not paths_path.exists():
            logger.error("Database files not found. Run 'build_database' first.")
            logger.error(f"Missing: {index_path} or {paths_path}")
            raise FileNotFoundError("Database files missing. Run 'build_database'.")

        logger.info(f"Loading database from {self.db_path}")
        try:
            self.index = faiss.read_index(str(index_path))
            logger.info(f"FAISS index loaded from {index_path}")

            with open(paths_path, "rb") as f:
                self.image_paths = pickle.load(f)
            logger.info(f"Image paths loaded from {paths_path}")
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            raise e

    def search(self, query: Union[str, Path], top_k: int = 5) -> List[str]:
        """
        Searches the database for images similar to the query (text or image path).

        Args:
            query (Union[str, Path]): The search query, either a text string or a path to an image.
            top_k (int): The number of most similar images to return.

        Returns:
            List[str]: A list of paths (as strings) to the most similar images,
                       ordered from highest to lowest similarity score.
        """
        if self.index is None or not self.image_paths:
            self._load_database()

        query_embedding: np.ndarray
        if os.path.isfile(query):  # Check if query is a path to an image file
            query_path = Path(query)
            logger.info(f"Searching for images similar to image: {query_path}")
            query_embedding = self._embed_image(query_path)
        else:  # Assume query is text
            text_query = str(query)
            logger.info(f"Searching for images similar to text: '{text_query}'")
            query_embedding = self._embed_text(text_query)

        # Normalize the query embedding if it wasn't already
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        query_embedding = query_embedding.astype("float32").reshape(
            1, -1
        )  # Shape (1, embedding_dim)

        # Perform the search using FAISS
        # For IndexFlatIP, scores are cosine similarities (higher is better)
        scores, indices = self.index.search(query_embedding, top_k)

        # Retrieve the corresponding image paths
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if 0 <= idx < len(self.image_paths):
                results.append(str(self.image_paths[idx]))

        logger.info(f"Search completed. Found {len(results)} results.")
        return results
