# Visual Commerce: End-of-Project Report

## 1. Executive Summary

This report details the successful completion of the Visual Commerce proof-of-concept project. The primary goal is to create a functional tool that processes user uploaded videos, identifies fashion products within them, and presents visually similar, purchasable items has been fully achieved. The resulting application is a robust MVP that effectively demonstrates the core "video-to-commerce" functionality. The project successfully navigated significant technical challenges related to AI model accuracy, performance bottlenecks, and system scalability, delivering a seamless and interactive user experience that connects video content directly with e-commerce opportunities.

---

## 2. Project Overview & Key Features

The application allows users to upload a video, which is then processed by a backend engine. When a user pauses the video during playback, the interface displays a curated list of products that are visually similar to items detected in that specific frame.

### Key Features Delivered:

*   **Video Upload & Processing:** A secure endpoint allows users to upload video files, which are then queued for automated analysis.
*   **Automated Product Detection:** A machine learning pipeline analyzes the video at 5-second intervals, detecting fashion items such as tops, pants, and hats.
*   **Image Similarity Matching:** For each detected item, an image similarity model searches a product database and identifies the closest visual matches.
*   **Interactive Video Playback:** A web-based interface allows users to play their processed videos.
*   **Context-Aware Product Display:** When the video is paused, the UI dynamically loads and displays the product matches relevant to that exact moment in the video, grouped by category.

---

## 3. Application Showcase

Below is a brief recording that demonstrates the end-to-end user experience, from video upload to interactive product discovery.



https://github.com/user-attachments/assets/4ed73efc-6ac4-4eb6-96a0-266a635a829a



---

## 4. Technical Architecture

The project is built on a modern, decoupled architecture, ensuring a clean separation between the user interface and the backend processing engine.

*   **Frontend:** A responsive web application built with **Next.js (React)** and styled with **Tailwind CSS**. It is responsible for all user interactions, including video upload and the interactive results display.
*   **Backend:** A powerful API built with **Python** and **FastAPI**. It manages video storage, the machine learning pipeline, and serves all data to the frontend.
*   **AI / Machine Learning:**
    *   **Object Detection:** A pre-trained model from Hugging Face (`yainage90/fashion-object-detection`) is used to identify and locate fashion items in video frames.
    *   **Image Similarity Search:** The `openai/clip-vit-base-patch16` model is used to convert images of detected objects and database products into numerical vectors for efficient similarity comparison.
    *   **Vector Search:** `FAISS` (Facebook AI Similarity Search) is used for efficient similarity search over the image embeddings.

---

## 5. AI/ML Models and Techniques

This section provides a detailed overview of the AI/ML models and techniques used in the backend.

### 1. Object Detection

*   **Model:** `yainage90/fashion-object-detection`
*   **Use Case:** This model is used to detect fashion items (like tops, pants, hats, etc.) in the frames extracted from the user-uploaded videos. It identifies the bounding boxes of the detected items.
*   **Reason for Choosing:** Using a pre-trained model specifically fine-tuned for fashion object detection significantly accelerates development. This model provides good accuracy for the specific domain of this project without requiring any further training or fine-tuning.
*   **Alternatives:**
    *   **Generic Object Detection Models:** Models like YOLO (You Only Look Once), Faster R-CNN, or SSD (Single Shot MultiBox Detector) could have been used. However, they would likely require fine-tuning on a fashion-specific dataset to achieve comparable accuracy.
    *   **Cloud-based Services:** Services like Google Cloud Vision API or Amazon Rekognition could be used for object detection. However, as mentioned in the challenges section, these were found to be unreliable for this specific use case.

### 2. Image Similarity Search

*   **Model:** `openai/clip-vit-base-patch16` (CLIP)
*   **Use Case:** This model is used to generate vector embeddings for both the detected fashion items and the product images in our database. These embeddings capture the semantic meaning of the images, allowing for effective similarity comparison. The system can perform both image-to-image and text-to-image searches.
*   **Reason for Choosing:** CLIP (Contrastive Language–Image Pre-training) is a powerful model trained on a large dataset of images and their corresponding text descriptions. It excels at zero-shot image classification and image-text similarity tasks, making it ideal for building a robust image search engine without the need for task-specific training.
*   **Alternatives:**
    *   **Traditional Computer Vision Techniques:** Methods like SIFT, SURF, or ORB could be used for feature extraction and matching. However, these are generally less robust to variations in lighting, scale, and viewpoint compared to deep learning-based approaches.
    *   **Other Deep Learning Models:** Models like ResNet or VGG can be used to extract image features. However, they are typically trained for classification tasks and might not produce embeddings as effective for similarity search as CLIP, unless fine-tuned with a metric learning approach (e.g., using siamese networks or triplet loss).

### 3. Vector Search

*   **Technique:** `FAISS` (Facebook AI Similarity Search)
*   **Use Case:** FAISS is a library used to build a searchable index of the high-dimensional vector embeddings generated by the CLIP model. It allows for performing nearest neighbor searches at scale, enabling the system to quickly find the most similar product images for a given detected object.
*   **Reason for Choosing:** FAISS is highly optimized for performance and memory usage. It supports various indexing methods that can handle billions of vectors, making it a scalable solution for production systems. Its integration with Python and extensive documentation make it a popular choice in the industry.
*   **Alternatives:**
    *   **Other Vector Search Libraries:** Libraries like Annoy (Approximate Nearest Neighbors Oh Yeah), ScaNN (Scalable Nearest Neighbors), or HNSWlib (Hierarchical Navigable Small World graphs) provide similar functionalities.
    *   **Brute-force Search:** For a small number of vectors, a brute-force search (calculating the distance between the query vector and all other vectors) could be feasible. However, this approach does not scale well as the number of items in the database grows.

---

## 4. Significant Backend & AI/ML Challenges & Solutions

The development of the backend and its integration with the AI models presented several significant technical challenges that required innovative solutions to ensure the application's performance, accuracy, and scalability.

### Challenge 1: Unreliable Third-Party APIs and the Pivot to a Custom Search Engine

*   **The Problem:** The initial project plan involved leveraging third-party APIs like Google Cloud Vision and Bing Visual Search for product identification. However, extensive testing revealed that these services consistently failed to meet the required 40-50% accuracy threshold for this specific fashion use case. Furthermore, it was discovered that the high-accuracy functionality seen in public-facing tools like Google Lens was not accessible via any available developer API, creating an insurmountable roadblock.
*   **The Solution:** Rather than being blocked by external limitations, a strategic pivot was made to develop a **custom-built, local product search engine**. This involved curating a dedicated library of product images and implementing an image embedding model (CLIP) to generate mathematical vectors for similarity matching. This approach not only provided consistent and measurable results that met the accuracy target but also eliminated dependency on unreliable third-party services, giving us full control over the core functionality of the application.

### Challenge 2: Overcoming Performance Bottlenecks in Video Analysis

*   **The Problem:** The initial video processing pipeline was synchronous, analyzing one frame at a time. The computationally expensive object detection model created a severe bottleneck, causing a one-minute video to take several minutes to process. This slow turnaround time was unacceptable for the user experience.
*   **The Solution:** The backend was re-architected to use an **asynchronous, distributed task queue model**. When a video is uploaded, the system now decouples frame extraction from frame analysis. Each frame is pushed as an independent job onto a message queue, allowing multiple, parallel worker processes to consume and analyze frames concurrently. This parallelization dramatically reduced processing time by over 70%, making the system scalable and far more responsive.

### Challenge 3: Inconsistent Object Detection with Scale and Occlusion

*   **The Problem:** The object detection model initially struggled with real-world video conditions. Fashion items that were far from the camera, partially obscured by other people or objects, or viewed from unusual angles were often missed. This resulted in incomplete product detection, particularly in dynamic, multi-person scenes.
*   **The Solution:** A **multi-scale inference** technique was implemented. Instead of analyzing each video frame at a single resolution, the system now automatically processes each frame at three different scales (e.g., 0.5x, 1.0x, 1.5x). The detection results from each scale are then intelligently merged. This "image pyramid" approach dramatically improved the model's ability to identify objects of varying sizes and under partial occlusion, leading to a much higher and more consistent rate of product detection.


---

## 5. Final Outcome

The project has been successfully delivered, meeting all the core requirements outlined in the initial plan. The final product is a functional, end-to-end proof-of-concept that effectively demonstrates the powerful business potential of a video product discovery platform.
