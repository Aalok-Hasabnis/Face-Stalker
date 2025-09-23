import face_recognition

import os



def find_person_in_images(reference_image_path, folder_path):

    """

    Find a person from reference image in multiple group photos

    

    Args:

        reference_image_path (str): Path to the reference image

        folder_path (str): Path to folder containing group images

    

    Returns:

        list: Filenames of images where the person is found

    """

    # Check if reference image exists

    if not os.path.exists(reference_image_path):

        print(f"Reference image not found: {reference_image_path}")

        return []

    

    # Check if folder exists

    if not os.path.exists(folder_path):

        print(f"Folder not found: {folder_path}")

        return []

    

    try:

        # Load reference image and encode the face

        print("Loading reference image...")

        reference_image = face_recognition.load_image_file(reference_image_path)

        reference_encodings = face_recognition.face_encodings(reference_image)

        

        if len(reference_encodings) == 0:

            print("No face found in the reference image!")

            return []

        

        reference_encoding = reference_encodings[0]

        print("Reference face loaded successfully!")

        

    except Exception as e:

        print(f"Error loading reference image: {e}")

        return []

    

    # List to store matching images

    matched_images = []

    

    # Get all image files

    image_files = [f for f in os.listdir(folder_path) 

                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]

    

    if not image_files:

        print("No image files found in the folder!")

        return []

    

    print(f"\nProcessing {len(image_files)} images...")

    

    # Iterate through all images in the folder

    for i, filename in enumerate(image_files, 1):

        print(f"Processing {i}/{len(image_files)}: {filename}")

        

        image_path = os.path.join(folder_path, filename)

        

        try:

            # Load group image

            group_image = face_recognition.load_image_file(image_path)

            group_encodings = face_recognition.face_encodings(group_image)

            

            if not group_encodings:

                print(f"  No faces detected in {filename}")

                continue

            

            print(f"  Found {len(group_encodings)} face(s)")

            

            # Compare each detected face with the reference

            for face_encoding in group_encodings:

                results = face_recognition.compare_faces([reference_encoding], face_encoding, tolerance=0.6)

                if results[0]:

                    matched_images.append(filename)

                    print(f"  ✓ Match found in {filename}!")

                    break  # No need to check more faces in this image

            

            if filename not in matched_images:

                print(f"  No match in {filename}")

                

        except Exception as e:

            print(f"  Error processing {filename}: {e}")

            continue

    

    return sorted(matched_images)



if __name__ == "__main__":

    # Example usage:

    reference_image_path = "reference.jpg"   # Path to the reference photo

    folder_path = "group_images"             # Folder with group photos

    

    print("Face Recognition Script Starting...")

    print("=" * 40)

    

    matches = find_person_in_images(reference_image_path, folder_path)

    

    print("\n" + "=" * 40)

    print("RESULTS:")

    

    if matches:

        print(f"Person found in {len(matches)} image(s):")

        for i, m in enumerate(matches, 1):

            print(f"{i}. {m}")

    else:

        print("Person not found in any images.")

    

    print("=" * 40)
