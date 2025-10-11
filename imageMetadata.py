# import os
# import json
# import re
# from typing import List, Dict, Any, Optional, Tuple
# from PIL import Image
# from PIL.ExifTags import TAGS
# import chromadb
# from chromadb.config import Settings
# from sentence_transformers import SentenceTransformer
# import numpy as np
# from pathlib import Path
# import hashlib
# from difflib import SequenceMatcher
# import face_recognition

# class FaceSimilarityDetector:
#     def __init__(self, db_path: str = "./chroma_db", use_face_recognition: bool = True):
#         """
#         Initialize the Face Similarity Detector
        
#         Args:
#             db_path: Path to ChromaDB storage
#             use_face_recognition: Whether to use face_recognition library for better face detection
#         """
#         self.db_path = db_path
#         self.use_face_recognition = use_face_recognition
        
#         # Initialize ChromaDB client
#         self.client = chromadb.PersistentClient(path=db_path)
        
#         # Create or get collections
#         self.image_collection = self.client.get_or_create_collection(
#             name="image_embeddings",
#             metadata={"description": "Face embeddings"}
#         )
        
#         self.metadata_collection = self.client.get_or_create_collection(
#             name="metadata_embeddings", 
#             metadata={"description": "Image metadata text embeddings"}
#         )
        
#         # Load models
#         if use_face_recognition:
#             print("Using face_recognition library for face embeddings...")
#         else:
#             print("Loading CLIP model...")
#             self.clip_model = SentenceTransformer("sentence-transformers/clip-ViT-B-32")
        
#         # For text embeddings from metadata
#         print("Loading text embedding model...")
#         self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        
#         print("Models loaded successfully!")
    
#     def extract_metadata(self, image_path: str) -> Dict[str, Any]:
#         """Extract metadata from image file"""
#         metadata = {
#             "filename": os.path.basename(image_path),
#             "file_size": os.path.getsize(image_path),
#             "file_extension": Path(image_path).suffix.lower()
#         }
        
#         try:
#             with Image.open(image_path) as img:
#                 metadata.update({
#                     "width": img.width,
#                     "height": img.height,
#                     "mode": img.mode,
#                     "format": img.format
#                 })
                
#                 # Extract EXIF data
#                 exif_data = img._getexif()
#                 if exif_data:
#                     exif_dict = {}
#                     for tag_id, value in exif_data.items():
#                         tag = TAGS.get(tag_id, tag_id)
#                         exif_dict[tag] = str(value)
#                     metadata["exif"] = exif_dict
                    
#         except Exception as e:
#             print(f"Error extracting metadata from {image_path}: {e}")
            
#         return metadata
    
#     def generate_face_embedding(self, image_path: str) -> Optional[np.ndarray]:
#         """Generate face embedding for an image"""
#         try:
#             if self.use_face_recognition:
#                 # Load image and find face encodings
#                 image = face_recognition.load_image_file(image_path)
#                 face_encodings = face_recognition.face_encodings(image)
                
#                 if len(face_encodings) > 0:
#                     # Return the first face encoding found
#                     return face_encodings[0]
#                 else:
#                     print(f"No face detected in {image_path}")
#                     return None
#             else:
#                 # Fallback to CLIP
#                 embedding = self.clip_model.encode(Image.open(image_path))
#                 return embedding
#         except Exception as e:
#             print(f"Error generating embedding for {image_path}: {e}")
#             return None
    
#     def generate_text_embedding(self, text: str) -> np.ndarray:
#         """Generate text embedding for metadata"""
#         try:
#             embedding = self.text_model.encode(text)
#             return embedding
#         except Exception as e:
#             print(f"Error generating text embedding: {e}")
#             return None
    
#     def extract_person_name_from_filename(self, filename: str) -> str:
#         """Extract person name from filename (e.g., 'hritik1.jpg' -> 'hritik')"""
#         # Remove extension
#         name_part = Path(filename).stem
#         # Remove numbers and common suffixes
#         person_name = re.sub(r'[0-9]+$', '', name_part).strip()
#         return person_name.lower()
    
#     def calculate_filename_similarity(self, filename1: str, filename2: str) -> float:
#         """Calculate similarity between two filenames based on person names"""
#         name1 = self.extract_person_name_from_filename(filename1)
#         name2 = self.extract_person_name_from_filename(filename2)
        
#         if name1 == name2 and name1 != "":
#             return 1.0
        
#         # Use sequence matcher for partial matches
#         similarity = SequenceMatcher(None, name1, name2).ratio()
#         return similarity
    
#     def create_metadata_text(self, metadata: Dict[str, Any]) -> str:
#         """Convert metadata dictionary to searchable text"""
#         text_parts = []
#         filename_base = Path(metadata["filename"]).stem
#         person_name = self.extract_person_name_from_filename(metadata["filename"])
        
#         text_parts.append(filename_base)
#         if person_name:
#             text_parts.append(person_name)
        
#         if "format" in metadata:
#             text_parts.append(f"format {metadata['format']}")
#         if "mode" in metadata:
#             text_parts.append(f"mode {metadata['mode']}")
        
#         if "exif" in metadata:
#             for key, value in metadata["exif"].items():
#                 if key in ["Make", "Model", "Software", "Artist", "Copyright", "ImageDescription"]:
#                     text_parts.append(f"{key} {value}")
        
#         return " ".join(text_parts)
    
#     def add_image(self, image_path: str, label: Optional[str] = None) -> bool:
#         """Add an image to the database with its embeddings"""
#         if not os.path.exists(image_path):
#             print(f"Image not found: {image_path}")
#             return False
        
#         try:
#             metadata = self.extract_metadata(image_path)
#             image_id = hashlib.md5(image_path.encode()).hexdigest()
            
#             face_embedding = self.generate_face_embedding(image_path)
#             if face_embedding is None:
#                 return False
            
#             person_name = self.extract_person_name_from_filename(metadata["filename"])
            
#             self.image_collection.add(
#                 embeddings=[face_embedding.tolist()],
#                 metadatas=[{
#                     "image_path": image_path,
#                     "filename": metadata["filename"],
#                     "person_name": person_name,
#                     "label": label or "",
#                     "type": "image"
#                 }],
#                 ids=[f"img_{image_id}"]
#             )
            
#             metadata_text = self.create_metadata_text(metadata)
#             if label:
#                 metadata_text += f" {label}"
                
#             metadata_embedding = self.generate_text_embedding(metadata_text)
#             if metadata_embedding is not None:
#                 self.metadata_collection.add(
#                     embeddings=[metadata_embedding.tolist()],
#                     metadatas=[{
#                         "image_path": image_path,
#                         "filename": metadata["filename"],
#                         "person_name": person_name,
#                         "metadata_text": metadata_text,
#                         "label": label or "",
#                         "type": "metadata"
#                     }],
#                     ids=[f"meta_{image_id}"]
#                 )
            
#             print(f"Successfully added: {metadata['filename']} (person: {person_name})")
#             return True
            
#         except Exception as e:
#             print(f"Error adding image {image_path}: {e}")
#             return False
    
#     def find_similar_faces(self, reference_image_path: str, n_results: int = 20, 
#                           similarity_threshold: float = 0.6, filename_weight: float = 0.3) -> List[Dict[str, Any]]:
#         """
#         Find faces similar to the reference image with filename-first logic
        
#         Args:
#             reference_image_path: Path to the reference image
#             n_results: Maximum number of results to return
#             similarity_threshold: Minimum similarity threshold (0.0 to 1.0)
#             filename_weight: Weight for filename similarity (0.0 to 1.0)
            
#         Returns:
#             List of dictionaries with filename and similarity score
#         """
#         if not os.path.exists(reference_image_path):
#             print(f"Reference image not found: {reference_image_path}")
#             return []
        
#         try:
#             print(f"Generating embedding for reference image: {reference_image_path}")
#             reference_embedding = self.generate_face_embedding(reference_image_path)
#             if reference_embedding is None:
#                 return []
            
#             reference_filename = os.path.basename(reference_image_path)
#             reference_person_name = self.extract_person_name_from_filename(reference_filename)
            
#             print("Searching for similar faces...")
#             results = self.image_collection.query(
#                 query_embeddings=[reference_embedding.tolist()],
#                 n_results=n_results
#             )
            
#             similar_faces = []
#             print(f"\nFound {len(results['metadatas'][0])} results:")
#             print("-" * 80)
            
#             for i, (metadata, distance) in enumerate(zip(results['metadatas'][0], results['distances'][0])):
#                 filename = metadata['filename']
                
#                 # Calculate face similarity (using cosine similarity for face_recognition)
#                 if self.use_face_recognition:
#                     # For face_recognition, distance is already a similarity measure (0-1, lower is more similar)
#                     face_similarity = max(0, 1 - distance)  # Convert to similarity score
#                 else:
#                     # For CLIP embeddings, convert distance to similarity
#                     face_similarity = max(0, 1 - distance)
                
#                 # Calculate filename similarity
#                 filename_similarity = self.calculate_filename_similarity(reference_filename, filename)
                
#                 # Combined similarity score
#                 combined_similarity = (1 - filename_weight) * face_similarity + filename_weight * filename_similarity
                
#                 print(f"{i+1:2d}. {filename:<20} | Face: {face_similarity:.3f} | Name: {filename_similarity:.3f} | Combined: {combined_similarity:.3f}")
                
#                 if combined_similarity >= similarity_threshold:
#                     similar_faces.append({
#                         'filename': filename,
#                         'face_similarity': face_similarity,
#                         'filename_similarity': filename_similarity,
#                         'combined_similarity': combined_similarity,
#                         'image_path': metadata['image_path'],
#                         'person_name': metadata.get('person_name', ''),
#                         'rank': i + 1
#                     })
            
#             # Sort by combined similarity score (highest first)
#             similar_faces.sort(key=lambda x: x['combined_similarity'], reverse=True)
            
#             print(f"\nFiltered results (combined similarity >= {similarity_threshold}):")
#             print("-" * 80)
#             if similar_faces:
#                 for face in similar_faces:
#                     print(f"✓ {face['filename']:<20} | Combined: {face['combined_similarity']:.3f} | Person: {face['person_name']}")
#             else:
#                 print(f"No faces found with combined similarity >= {similarity_threshold}")
#                 print("Try lowering the threshold or check if the reference image is in the database")
            
#             return similar_faces
            
#         except Exception as e:
#             print(f"Error finding similar faces: {e}")
#             return []
    
#     def search_by_filename_similarity(self, filename: str, n_results: int = 10, 
#                                     similarity_threshold: float = 0.6, filename_weight: float = 0.3) -> List[Dict[str, Any]]:
#         """
#         Find images similar to a file already in the database
        
#         Args:
#             filename: Name of the file to find similar images for
#             n_results: Maximum number of results
#             similarity_threshold: Minimum similarity threshold
#             filename_weight: Weight for filename similarity
            
#         Returns:
#             List of similar images with metadata
#         """
#         try:
#             # Find the image in the database
#             db_results = self.image_collection.get(where={"filename": filename})
            
#             if not db_results['metadatas']:
#                 print(f"Filename '{filename}' not found in database")
#                 available_files = self.list_all_filenames()
#                 print(f"Available files: {available_files[:10]}...")
#                 return []
            
#             # Get the embedding for this image
#             image_path = db_results['metadatas'][0]['image_path']
#             if not os.path.exists(image_path):
#                 print(f"Original image file not found: {image_path}")
#                 return []
            
#             return self.find_similar_faces(image_path, n_results, similarity_threshold, filename_weight)
            
#         except Exception as e:
#             print(f"Error searching by filename: {e}")
#             return []
    
#     def find_by_person_name(self, person_name: str, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
#         """Find all images of a specific person by name"""
#         try:
#             person_name = person_name.lower()
#             results = self.image_collection.get()
            
#             matching_images = []
#             for metadata in results['metadatas']:
#                 stored_person_name = metadata.get('person_name', '').lower()
#                 if stored_person_name == person_name or person_name in stored_person_name:
#                     matching_images.append({
#                         'filename': metadata['filename'],
#                         'person_name': stored_person_name,
#                         'image_path': metadata['image_path']
#                     })
            
#             print(f"Found {len(matching_images)} images for person '{person_name}':")
#             for img in matching_images:
#                 print(f"  - {img['filename']}")
            
#             return matching_images
            
#         except Exception as e:
#             print(f"Error finding images by person name: {e}")
#             return []
    
#     def add_images_from_directory(self, directory_path: str, label: Optional[str] = None) -> None:
#         """Add all images from a directory to the database"""
#         if not os.path.exists(directory_path):
#             print(f"Directory not found: {directory_path}")
#             return
        
#         image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
#         added_count = 0
        
#         for filename in os.listdir(directory_path):
#             if Path(filename).suffix.lower() in image_extensions:
#                 image_path = os.path.join(directory_path, filename)
#                 if self.add_image(image_path, label):
#                     added_count += 1
        
#         print(f"Added {added_count} images from {directory_path}")
    
#     def get_collection_stats(self) -> Dict[str, int]:
#         """Get statistics about the collections"""
#         return {
#             "total_images": self.image_collection.count(),
#             "total_metadata": self.metadata_collection.count()
#         }
    
#     def list_all_filenames(self) -> List[str]:
#         """Get all filenames in the database"""
#         try:
#             results = self.image_collection.get()
#             return [metadata['filename'] for metadata in results['metadatas']]
#         except Exception as e:
#             print(f"Error retrieving filenames: {e}")
#             return []

# def main():
#     # Initialize the detector with face_recognition for better face detection
#     detector = FaceSimilarityDetector(use_face_recognition=True)
    
#     # Check if database already has images
#     stats = detector.get_collection_stats()
#     print("Database statistics:", stats)
    
#     # Clear existing database if it has incompatible embeddings
#     if stats["total_images"] > 0:
#         print("\nClearing existing database due to embedding dimension mismatch...")
#         detector.client.delete_collection("image_embeddings")
#         detector.client.delete_collection("metadata_embeddings")
#         # Recreate collections
#         detector.image_collection = detector.client.get_or_create_collection(
#             name="image_embeddings",
#             metadata={"description": "Face embeddings"}
#         )
#         detector.metadata_collection = detector.client.get_or_create_collection(
#             name="metadata_embeddings", 
#             metadata={"description": "Image metadata text embeddings"}
#         )
#         stats = detector.get_collection_stats()
#         print(f"Database cleared. New stats: {stats}")
    
#     # If no images in database, add them
#     if stats["total_images"] == 0:
#         print("\nAdding reference image...")
#         detector.add_image("hritik.jpg", "hritik_roshan")
        
#         print("\nAdding images from group_images directory...")
#         detector.add_images_from_directory("group_images", "group_photos")
    
#     # Method 1: Use the reference image file directly with higher filename weight
#     print("\n" + "="*80)
#     print("METHOD 1: Using reference image with filename-first logic")
#     print("="*80)
    
#     similar_faces_method1 = detector.find_similar_faces(
#         reference_image_path="hritik.jpg",
#         n_results=20,
#         similarity_threshold=0.4,
#         filename_weight=0.4  # Give more weight to filename similarity
#     )
    
#     # Method 2: Find all images by person name
#     print("\n" + "="*80)
#     print("METHOD 2: Finding all images by person name")
#     print("="*80)
    
#     hritik_images = detector.find_by_person_name("hritik")
    
#     # Method 3: Search by filename similarity
#     print("\n" + "="*80)
#     print("METHOD 3: Using filename from database")
#     print("="*80)
    
#     similar_faces_method3 = detector.search_by_filename_similarity(
#         filename="hritik.jpg",
#         n_results=15,
#         similarity_threshold=0.5,
#         filename_weight=0.4
#     )
    
#     # Show summary
#     print("\n" + "="*80)
#     print("SUMMARY")
#     print("="*80)
    
#     if similar_faces_method1:
#         hritik_images_found = [face['filename'] for face in similar_faces_method1 if 'hritik' in face['filename'].lower()]
#         other_images = [face['filename'] for face in similar_faces_method1 if 'hritik' not in face['filename'].lower()]
        
#         print(f"\nTotal similar images found: {len(similar_faces_method1)}")
#         print(f"Images with 'hritik' in filename: {len(hritik_images_found)}")
#         print(f"Other similar images: {len(other_images)}")
        
#         if hritik_images_found:
#             print(f"\nHritik images found: {hritik_images_found}")
#         if other_images:
#             print(f"Other similar faces: {other_images}")
#     else:
#         print("No similar faces found. Try lowering the similarity threshold.")
    
#     # List all available files for reference
#     print(f"\nAll files in database (grouped by person):")
#     all_files = detector.list_all_filenames()
#     person_groups = {}
    
#     for filename in sorted(all_files):
#         person_name = detector.extract_person_name_from_filename(filename)
#         if person_name not in person_groups:
#             person_groups[person_name] = []
#         person_groups[person_name].append(filename)
    
#     for person, files in person_groups.items():
#         print(f"\n{person.upper()}: {files}")

# if __name__ == "__main__":
#     main()


import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
from PIL.ExifTags import TAGS
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path
import hashlib
from difflib import SequenceMatcher
import face_recognition

class FaceSimilarityDetector:
    def __init__(self, db_path: str = "./chroma_db", use_face_recognition: bool = True):
        """
        Initialize the Face Similarity Detector
        
        Args:
            db_path: Path to ChromaDB storage
            use_face_recognition: Whether to use face_recognition library for better face detection
        """
        self.db_path = db_path
        self.use_face_recognition = use_face_recognition
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Create or get collections
        self.image_collection = self.client.get_or_create_collection(
            name="image_embeddings",
            metadata={"description": "Face embeddings"}
        )
        
        self.metadata_collection = self.client.get_or_create_collection(
            name="metadata_embeddings", 
            metadata={"description": "Image metadata text embeddings"}
        )
        
        # Load models
        if use_face_recognition:
            print("Using face_recognition library for face embeddings...")
        else:
            print("Loading CLIP model...")
            self.clip_model = SentenceTransformer("sentence-transformers/clip-ViT-B-32")
        
        # For text embeddings from metadata
        print("Loading text embedding model...")
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("Models loaded successfully!")
    
    def extract_metadata(self, image_path: str) -> Dict[str, Any]:
        """Extract metadata from image file"""
        metadata = {
            "filename": os.path.basename(image_path),
            "file_size": os.path.getsize(image_path),
            "file_extension": Path(image_path).suffix.lower()
        }
        
        try:
            with Image.open(image_path) as img:
                metadata.update({
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode,
                    "format": img.format
                })
                
                # Extract EXIF data
                exif_data = img._getexif()
                if exif_data:
                    exif_dict = {}
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_dict[tag] = str(value)
                    metadata["exif"] = exif_dict
                    
        except Exception as e:
            print(f"Error extracting metadata from {image_path}: {e}")
            
        return metadata
    
    def generate_face_embedding(self, image_path: str) -> Optional[np.ndarray]:
        """Generate face embedding for an image"""
        try:
            if self.use_face_recognition:
                # Load image and find face encodings
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)
                
                if len(face_encodings) > 0:
                    # Return the first face encoding found
                    return face_encodings[0]
                else:
                    print(f"No face detected in {image_path}")
                    return None
            else:
                # Fallback to CLIP
                embedding = self.clip_model.encode(Image.open(image_path))
                return embedding
        except Exception as e:
            print(f"Error generating embedding for {image_path}: {e}")
            return None
    
    def generate_text_embedding(self, text: str) -> np.ndarray:
        """Generate text embedding for metadata"""
        try:
            embedding = self.text_model.encode(text)
            return embedding
        except Exception as e:
            print(f"Error generating text embedding: {e}")
            return None
    
    def extract_person_name_from_filename(self, filename: str) -> str:
        """Extract person name from filename (e.g., 'hritik1.jpg' -> 'hritik')"""
        # Remove extension
        name_part = Path(filename).stem
        # Remove numbers and common suffixes
        person_name = re.sub(r'[0-9]+$', '', name_part).strip()
        return person_name.lower()
    
    def calculate_filename_similarity(self, filename1: str, filename2: str) -> float:
        """Calculate similarity between two filenames based on person names"""
        name1 = self.extract_person_name_from_filename(filename1)
        name2 = self.extract_person_name_from_filename(filename2)
        
        if name1 == name2 and name1 != "":
            return 1.0
        
        # Use sequence matcher for partial matches
        similarity = SequenceMatcher(None, name1, name2).ratio()
        return similarity
    
    def create_metadata_text(self, metadata: Dict[str, Any]) -> str:
        """Convert metadata dictionary to searchable text"""
        text_parts = []
        filename_base = Path(metadata["filename"]).stem
        person_name = self.extract_person_name_from_filename(metadata["filename"])
        
        text_parts.append(filename_base)
        if person_name:
            text_parts.append(person_name)
        
        if "format" in metadata:
            text_parts.append(f"format {metadata['format']}")
        if "mode" in metadata:
            text_parts.append(f"mode {metadata['mode']}")
        
        if "exif" in metadata:
            for key, value in metadata["exif"].items():
                if key in ["Make", "Model", "Software", "Artist", "Copyright", "ImageDescription"]:
                    text_parts.append(f"{key} {value}")
        
        return " ".join(text_parts)
    
    def add_image(self, image_path: str, label: Optional[str] = None) -> bool:
        """Add an image to the database with its embeddings"""
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            return False
        
        try:
            metadata = self.extract_metadata(image_path)
            image_id = hashlib.md5(image_path.encode()).hexdigest()
            
            face_embedding = self.generate_face_embedding(image_path)
            if face_embedding is None:
                return False
            
            person_name = self.extract_person_name_from_filename(metadata["filename"])
            
            self.image_collection.add(
                embeddings=[face_embedding.tolist()],
                metadatas=[{
                    "image_path": image_path,
                    "filename": metadata["filename"],
                    "person_name": person_name,
                    "label": label or "",
                    "type": "image"
                }],
                ids=[f"img_{image_id}"]
            )
            
            metadata_text = self.create_metadata_text(metadata)
            if label:
                metadata_text += f" {label}"
                
            metadata_embedding = self.generate_text_embedding(metadata_text)
            if metadata_embedding is not None:
                self.metadata_collection.add(
                    embeddings=[metadata_embedding.tolist()],
                    metadatas=[{
                        "image_path": image_path,
                        "filename": metadata["filename"],
                        "person_name": person_name,
                        "metadata_text": metadata_text,
                        "label": label or "",
                        "type": "metadata"
                    }],
                    ids=[f"meta_{image_id}"]
                )
            
            print(f"Successfully added: {metadata['filename']} (person: {person_name})")
            return True
            
        except Exception as e:
            print(f"Error adding image {image_path}: {e}")
            return False
    
    def find_similar_faces(self, reference_image_path: str, n_results: int = 20, 
                          similarity_threshold: float = 0.6, filename_weight: float = 0.3) -> List[Dict[str, Any]]:
        """
        Find faces similar to the reference image with filename-first logic
        
        Args:
            reference_image_path: Path to the reference image
            n_results: Maximum number of results to return
            similarity_threshold: Minimum similarity threshold (0.0 to 1.0)
            filename_weight: Weight for filename similarity (0.0 to 1.0)
            
        Returns:
            List of dictionaries with filename and similarity score
        """
        if not os.path.exists(reference_image_path):
            print(f"Reference image not found: {reference_image_path}")
            return []
        
        try:
            print(f"Generating embedding for reference image: {reference_image_path}")
            reference_embedding = self.generate_face_embedding(reference_image_path)
            if reference_embedding is None:
                return []
            
            reference_filename = os.path.basename(reference_image_path)
            reference_person_name = self.extract_person_name_from_filename(reference_filename)
            
            print("Searching for similar faces...")
            results = self.image_collection.query(
                query_embeddings=[reference_embedding.tolist()],
                n_results=n_results
            )
            
            similar_faces = []
            print(f"\nFound {len(results['metadatas'][0])} results:")
            print("-" * 80)
            
            for i, (metadata, distance) in enumerate(zip(results['metadatas'][0], results['distances'][0])):
                filename = metadata['filename']
                
                # Calculate face similarity (using cosine similarity for face_recognition)
                if self.use_face_recognition:
                    # For face_recognition, distance is already a similarity measure (0-1, lower is more similar)
                    face_similarity = max(0, 1 - distance)  # Convert to similarity score
                else:
                    # For CLIP embeddings, convert distance to similarity
                    face_similarity = max(0, 1 - distance)
                
                # Calculate filename similarity
                filename_similarity = self.calculate_filename_similarity(reference_filename, filename)
                
                # Combined similarity score
                combined_similarity = (1 - filename_weight) * face_similarity + filename_weight * filename_similarity
                
                print(f"{i+1:2d}. {filename:<20} | Face: {face_similarity:.3f} | Name: {filename_similarity:.3f} | Combined: {combined_similarity:.3f}")
                
                if combined_similarity >= similarity_threshold:
                    similar_faces.append({
                        'filename': filename,
                        'face_similarity': face_similarity,
                        'filename_similarity': filename_similarity,
                        'combined_similarity': combined_similarity,
                        'image_path': metadata['image_path'],
                        'person_name': metadata.get('person_name', ''),
                        'rank': i + 1
                    })
            
            # Sort by combined similarity score (highest first)
            similar_faces.sort(key=lambda x: x['combined_similarity'], reverse=True)
            
            print(f"\nFiltered results (combined similarity >= {similarity_threshold}):")
            print("-" * 80)
            if similar_faces:
                for face in similar_faces:
                    print(f"✓ {face['filename']:<20} | Combined: {face['combined_similarity']:.3f} | Person: {face['person_name']}")
            else:
                print(f"No faces found with combined similarity >= {similarity_threshold}")
                print("Try lowering the threshold or check if the reference image is in the database")
            
            return similar_faces
            
        except Exception as e:
            print(f"Error finding similar faces: {e}")
            return []
    
    def print_dual_categorization_summary(self, similar_faces: List[Dict[str, Any]], 
                                         reference_filename: str, 
                                         face_similarity_threshold: float = 0.5):
        """
        Print a summary with dual categorization: by face similarity and by filename
        
        Args:
            similar_faces: List of similar faces from find_similar_faces()
            reference_filename: Name of the reference image file
            face_similarity_threshold: Threshold for considering faces as matching
        """
        if not similar_faces:
            print("No similar faces found. Try lowering the similarity threshold.")
            return
        
        reference_person_name = self.extract_person_name_from_filename(reference_filename)
        
        print("\n" + "="*80)
        print("SUMMARY - Dual Categorization")
        print("="*80)
        print(f"\nReference: {reference_filename} (Person: {reference_person_name})")
        print(f"Total similar faces found: {len(similar_faces)}")
        
        # Section 1: Group by face similarity
        print("\n📊 GROUPED BY FACE SIMILARITY (who they look like):")
        print(f"└─ {reference_person_name.upper()} FACES (face matches {reference_person_name}):")
        for face in similar_faces:
            match_indicator = "✓" if reference_person_name in face['filename'].lower() else "⚠️ "
            print(f"   {match_indicator} {face['filename']:<25} (face: {face['face_similarity']:.3f}, name: {face['filename_similarity']:.3f})")
        
        # Section 2: Group by filename/person name
        print(f"\n📁 GROUPED BY FILENAME (how they're labeled):")
        filename_groups = {}
        for face in similar_faces:
            person_name = face['person_name'] or 'unknown'
            if person_name not in filename_groups:
                filename_groups[person_name] = []
            filename_groups[person_name].append(face)
        
        for person_name, faces in sorted(filename_groups.items()):
            is_reference_group = person_name == reference_person_name
            prefix = "└─" if is_reference_group else "├─"
            print(f"{prefix} {person_name.upper()} folder ({len(faces)} images):")
            for face in faces:
                print(f"   • {face['filename']:<25} (combined: {face['combined_similarity']:.3f})")
        
        # Section 3: Potential mislabeling detection
        print(f"\n⚠️  POTENTIAL MISLABELING DETECTED:")
        mislabeled = [f for f in similar_faces 
                     if reference_person_name not in f['filename'].lower() 
                     and f['face_similarity'] > face_similarity_threshold]
        if mislabeled:
            print(f"   These images look like {reference_person_name} but aren't named as such:")
            for face in mislabeled:
                print(f"   ⚠️  {face['filename']:<25} in '{face['person_name']}' folder (face similarity: {face['face_similarity']:.3f})")
        else:
            print("   None detected - all labels match face recognition!")
    
    def search_by_filename_similarity(self, filename: str, n_results: int = 10, 
                                    similarity_threshold: float = 0.6, filename_weight: float = 0.3) -> List[Dict[str, Any]]:
        """
        Find images similar to a file already in the database
        
        Args:
            filename: Name of the file to find similar images for
            n_results: Maximum number of results
            similarity_threshold: Minimum similarity threshold
            filename_weight: Weight for filename similarity
            
        Returns:
            List of similar images with metadata
        """
        try:
            # Find the image in the database
            db_results = self.image_collection.get(where={"filename": filename})
            
            if not db_results['metadatas']:
                print(f"Filename '{filename}' not found in database")
                available_files = self.list_all_filenames()
                print(f"Available files: {available_files[:10]}...")
                return []
            
            # Get the embedding for this image
            image_path = db_results['metadatas'][0]['image_path']
            if not os.path.exists(image_path):
                print(f"Original image file not found: {image_path}")
                return []
            
            return self.find_similar_faces(image_path, n_results, similarity_threshold, filename_weight)
            
        except Exception as e:
            print(f"Error searching by filename: {e}")
            return []
    
    def find_by_person_name(self, person_name: str, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find all images of a specific person by name"""
        try:
            person_name = person_name.lower()
            results = self.image_collection.get()
            
            matching_images = []
            for metadata in results['metadatas']:
                stored_person_name = metadata.get('person_name', '').lower()
                if stored_person_name == person_name or person_name in stored_person_name:
                    matching_images.append({
                        'filename': metadata['filename'],
                        'person_name': stored_person_name,
                        'image_path': metadata['image_path']
                    })
            
            print(f"Found {len(matching_images)} images for person '{person_name}':")
            for img in matching_images:
                print(f"  - {img['filename']}")
            
            return matching_images
            
        except Exception as e:
            print(f"Error finding images by person name: {e}")
            return []
    
    def add_images_from_directory(self, directory_path: str, label: Optional[str] = None) -> None:
        """Add all images from a directory to the database"""
        if not os.path.exists(directory_path):
            print(f"Directory not found: {directory_path}")
            return
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        added_count = 0
        
        for filename in os.listdir(directory_path):
            if Path(filename).suffix.lower() in image_extensions:
                image_path = os.path.join(directory_path, filename)
                if self.add_image(image_path, label):
                    added_count += 1
        
        print(f"Added {added_count} images from {directory_path}")
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics about the collections"""
        return {
            "total_images": self.image_collection.count(),
            "total_metadata": self.metadata_collection.count()
        }
    
    def list_all_filenames(self) -> List[str]:
        """Get all filenames in the database"""
        try:
            results = self.image_collection.get()
            return [metadata['filename'] for metadata in results['metadatas']]
        except Exception as e:
            print(f"Error retrieving filenames: {e}")
            return []

def main():
    # Initialize the detector with face_recognition for better face detection
    detector = FaceSimilarityDetector(use_face_recognition=True)
    
    # Check if database already has images
    stats = detector.get_collection_stats()
    print("Database statistics:", stats)
    
    # Clear existing database if it has incompatible embeddings
    if stats["total_images"] > 0:
        print("\nClearing existing database due to embedding dimension mismatch...")
        detector.client.delete_collection("image_embeddings")
        detector.client.delete_collection("metadata_embeddings")
        # Recreate collections
        detector.image_collection = detector.client.get_or_create_collection(
            name="image_embeddings",
            metadata={"description": "Face embeddings"}
        )
        detector.metadata_collection = detector.client.get_or_create_collection(
            name="metadata_embeddings", 
            metadata={"description": "Image metadata text embeddings"}
        )
        stats = detector.get_collection_stats()
        print(f"Database cleared. New stats: {stats}")
    
    # If no images in database, add them
    if stats["total_images"] == 0:
        print("\nAdding reference image...")
        detector.add_image("hritik.jpg", "hritik_roshan")
        
        print("\nAdding images from group_images directory...")
        detector.add_images_from_directory("group_images", "group_photos")
    
    # Method 1: Use the reference image file directly with higher filename weight
    print("\n" + "="*80)
    print("METHOD 1: Using reference image with filename-first logic")
    print("="*80)
    
    reference_image = "hritik.jpg"  # Change this to any reference image
    similar_faces_method1 = detector.find_similar_faces(
        reference_image_path=reference_image,
        n_results=20,
        similarity_threshold=0.4,
        filename_weight=0.4  # Give more weight to filename similarity
    )
    
    # Method 2: Find all images by person name
    print("\n" + "="*80)
    print("METHOD 2: Finding all images by person name")
    print("="*80)
    
    reference_person = detector.extract_person_name_from_filename(reference_image)
    person_images = detector.find_by_person_name(reference_person)
    
    # Method 3: Search by filename similarity
    print("\n" + "="*80)
    print("METHOD 3: Using filename from database")
    print("="*80)
    
    similar_faces_method3 = detector.search_by_filename_similarity(
        filename=reference_image,
        n_results=15,
        similarity_threshold=0.5,
        filename_weight=0.4
    )
    
    # Print dual categorization summary
    detector.print_dual_categorization_summary(
        similar_faces=similar_faces_method1,
        reference_filename=reference_image,
        face_similarity_threshold=0.5
    )
    
    # List all available files for reference
    print(f"\n" + "="*80)
    print(f"ALL FILES IN DATABASE (grouped by person)")
    print("="*80)
    all_files = detector.list_all_filenames()
    person_groups = {}
    
    for filename in sorted(all_files):
        person_name = detector.extract_person_name_from_filename(filename)
        if person_name not in person_groups:
            person_groups[person_name] = []
        person_groups[person_name].append(filename)
    
    for person, files in person_groups.items():
        print(f"\n{person.upper()}: {files}")

if __name__ == "__main__":
    main()