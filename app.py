from flask import Flask, render_template, request, jsonify
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import io
import base64
from groq import Groq
from deep_translator import GoogleTranslator

app = Flask(__name__)

# Load model and labels (with error handling for missing files)
try:
    model = load_model("keras_model.h5", compile=False)
    class_names = open("labels.txt", "r").readlines()
except:
    model = None
    class_names = []

# Medication suggestions for specific diseases
medications = {
    "1 LUMPY SKIN": "Tips for Lumpy Skin Disease (LSD):"
                    "Isolation: Immediately isolate affected animals to prevent the spread of the disease to other livestock."
                    "Hygiene: Maintain a clean environment by disinfecting animal housing, feeding equipment, and water troughs regularly."
                    "Supportive Care: Ensure animals are well-fed with a nutritious diet to strengthen their immune systems. Providing fresh, clean water is essential."
                    "Reduce Stress: Keep the animals in a calm and stress-free environment. Stress can worsen disease symptoms."
                    "Monitor for Secondary Infections: Keep an eye on skin lesions and prevent further infection by cleaning any open wounds.",
    "4 RINGWORM": "Management Tips for Ringworm:"
                    "Isolate Infected Animals to prevent spread."
                    "Maintain Cleanliness by changing bedding and disinfecting equipment."
                    "Improve Nutrition with a balanced diet and supplements like zinc and vitamin A."
                    "Use Topical Antifungal Ointments like clotrimazole or sulfur dips."
                    "Sun Exposure can help kill fungi."
                    "Groom Regularly to remove scabs and infected fur."
                    "Reduce Stress by providing a comfortable environment."
                    "Monitor Other Animals for signs and consult a vet if needed.",
    "6 MASTITIS": "Tips and management for Mastitis"
                    "Frequent Milking: Regular milking helps prevent milk build-up and reduces the chances of infection."
                    "Proper Hygiene: Clean the udder and teats before and after milking to prevent bacterial entry. Use sanitized towels and gloves."
                    "Dry Cow Therapy: After the lactating period, administer dry cow therapy to prevent mastitis and keep the udder healthy."
                    "Diet Management: Ensure a balanced nutrition with adequate amounts of vitamins and minerals to maintain good udder health."
                    "Massaging: Gently massage the udder to improve circulation and promote milk flow, which can help reduce the risk of mastitis.",
    "3 SHEEP SCABIES": "Tips for Sheep Scabies (For Mouth Area)"
                        "Keep Sheep Clean: Regularly bathe the sheep in mild antiseptic solutions to help remove mites from the skin."
                        "Maintain Bedding: Change bedding frequently to prevent mite infestations. Clean the stalls with a disinfectant to kill any remaining mites."
                        "Improve Nutrition: Provide a balanced diet with minerals and vitamins that help strengthen the immune system and promote skin healing."
                        "Reduce Stress: Avoid overcrowding, and provide adequate space, ventilation, and quiet surroundings to reduce stress, which can worsen scabies."
                        "Skin Care: Apply soothing oils like neem oil or coconut oil to the affected areas, especially around the mouth, to help calm irritation and moisturize the skin."
                        "Monitor and Isolate: Isolate any affected animals to prevent the spread of the disease to healthy sheep.",
    "10 GREASY DISEASE": "Prevention and Management Tips for Greasy Disease:"
                        "Clean and Dry Conditions: Keep pens and bedding dry to prevent bacterial growth."
                        "Isolate: Separate infected pigs to avoid spreading."
                        "Boost Immunity: Provide a balanced diet with vitamins A, E, and omega-3 fatty acids."
                        "Skin Care: Clean affected areas with antiseptic and apply antibacterial ointments."
                        "Herbal Remedies: Use neem oil and turmeric paste for their antibacterial properties."
                        "Hydration: Ensure access to fresh, clean water."
                        "Monitor: Watch for early signs and isolate any affected animals."
}

# Initialize Groq client (Replace with your actual API key)
API_KEY = "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"
client = Groq(api_key=API_KEY)

def translate_text(text, target_language):
    """Translates text to the specified target language."""
    try:
        return GoogleTranslator(source="auto", target=target_language).translate(text)
    except:
        return text

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/rearing-guidance")
def rearing_guidance():
    return render_template('s1.html')

@app.route('/result', methods=['POST'])
def result():
    # Get user input
    animal_type = request.form['animal_type']
    number_of_animals = int(request.form['number_of_animals'])
    
    # Map animal type and count to required features
    area_size, feed_type, feed_quantity, cost_in_inr, water_supply, hygiene_tips, seasonal_tips = get_animal_data(animal_type, number_of_animals)

    return render_template('s1.html',
                           area_size=area_size,
                           feed_type=feed_type,
                           feed_quantity=feed_quantity,
                           cost_in_inr=cost_in_inr,
                           water_supply=water_supply,
                           hygiene_tips=hygiene_tips,
                           seasonal_tips=seasonal_tips,
                           animal_type=animal_type,
                           number_of_animals=number_of_animals,
                           )

# Helper function to map animal type and count to required values
def get_animal_data(animal_type, count):
    if animal_type == 'Cow':
        area_size = 19.81 * count
        feed_type = 'Green Feed'
        feed_quantity = 24.85 * count
        cost_in_inr = 6652.15 * count
        water_supply = 68.52 * count
        hygiene_tips = 'Clean barn daily, vaccinate regularly'
        seasonal_tips = 'Summer: Provide shade and cool water, Winter: Ensure warmth, Rainy: Avoid damp areas.'
    elif animal_type == 'Buffalo':
        area_size = 24.58 * count
        feed_type = 'Dry Feed'
        feed_quantity = 31.45 * count
        cost_in_inr = 7483.52 * count
        water_supply = 81.23 * count
        hygiene_tips = 'Ensure proper ventilation'
        seasonal_tips = 'Summer: Provide shade and cool water, Winter: Provide shelter, Rainy: Dry bedding is essential.'
    elif animal_type == 'Pig':
        area_size = 15.25 * count
        feed_type = 'Concentrates'
        feed_quantity = 5.15 * count
        cost_in_inr = 4989.25 * count
        water_supply = 50.60 * count
        hygiene_tips = 'Use disinfectants weekly'
        seasonal_tips = 'Summer: Keep cool and dry, Winter: Ensure warmth, Rainy: Keep pens dry.'
    elif animal_type == 'Goat':
        area_size = 10.21 * count
        feed_type = 'Green Feed'
        feed_quantity = 3.25 * count
        cost_in_inr = 3325.60 * count
        water_supply = 20.55 * count
        hygiene_tips = 'Provide clean bedding'
        seasonal_tips = 'Summer: Provide fresh water and shade, Winter: Ensure dry and warm shelter, Rainy: Avoid damp areas.'
    elif animal_type == 'Sheep':
        area_size = 12.50 * count
        feed_type = 'Green Feed'
        feed_quantity = 4.75 * count
        cost_in_inr = 3741.75 * count
        water_supply = 25.80 * count
        hygiene_tips = 'Check for parasites regularly'
        seasonal_tips = 'Summer: Provide plenty of water, Winter: Keep warm with shelter, Rainy: Keep dry and prevent wool rot.'
    elif animal_type == 'Poultry':
        area_size = 1.5 * count
        feed_type = 'Grain-based Feed'
        feed_quantity = 0.25 * count
        cost_in_inr = 120 * count
        water_supply = 0.5 * count
        hygiene_tips = 'Keep the coop clean and free from pests'
        seasonal_tips = 'Summer: Ensure proper ventilation, Winter: Provide heat and protection, Rainy: Keep the coop dry.'
    elif animal_type == 'Bee Hiving':
        area_size = 10.25  # In square feet, for a beekeeping area
        feed_type = 'Sugar Syrup'
        feed_quantity = 0.5 * count  # For hives
        cost_in_inr = 1500.55 * count  # Cost per hive
        water_supply = 0.25 * count  # Water requirement per hive
        hygiene_tips = 'Check for pests like mites and wax moths'
        seasonal_tips = 'Summer: Provide ample water sources, Winter: Ensure the bees have enough food stores, Rainy: Avoid disturbances.'
    elif animal_type == 'Sericulture':
        area_size = 4.85 * count  # In square feet, for silkworms
        feed_type = 'Mulberry Leaves'
        feed_quantity = 0.1 * count  # Per silkworm
        cost_in_inr = 198.25 * count  # Cost per silkworm
        water_supply = 0.2 * count  # Water per silkworm
        hygiene_tips = 'Maintain clean environment, avoid humidity'
        seasonal_tips = 'Summer: Maintain cool and dry conditions, Winter: Keep warm, Rainy: Ensure adequate airflow.'

    return area_size, feed_type, feed_quantity, cost_in_inr, water_supply, hygiene_tips, seasonal_tips

@app.route("/ai-chatbot")
def ai_chatbot():
    return render_template("s2.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")  # Get user's message
    target_language = data.get("language", "en")  # Get target language (default: English)

    try:
        # Translate user input to English before sending it to the chatbot
        user_message_en = translate_text(user_message, "en")

        # Use Groq API to get a response from the chatbot
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": user_message_en}],
            model="llama-3.3-70b-versatile"  # Replace with the correct Groq model
        )

        bot_response_en = response.choices[0].message.content  # Extract chatbot's response

        # Translate bot response back to the selected language
        bot_response_translated = translate_text(bot_response_en, target_language)

        return jsonify({"response": bot_response_translated})

    except Exception as e:
        return jsonify({"response": "Sorry, there was an error. Try again later!"})

@app.route("/disease-detection", methods=["GET", "POST"])
def disease_detection():
    prediction = None
    confidence = None
    medication = None
    img_data = None  # Variable to store image data for displaying on the webpage
    if request.method == "POST":
        # Check if image file is provided
        if "file" not in request.files:
            return render_template("s3.html", error="No file part")

        file = request.files["file"]
        if file.filename == "":
            return render_template("s3.html", error="No selected file")

        if file and model is not None:
            # Process the image
            image = Image.open(file).convert("RGB")

            # Resize the image to 224x224 and crop from the center
            size = (224, 224)
            image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

            # Convert image to numpy array and normalize
            image_array = np.asarray(image)
            normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

            # Create the array of the right shape to feed into the keras model
            data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
            data[0] = normalized_image_array

            # Predict the model
            prediction = model.predict(data)
            index = np.argmax(prediction)
            class_name = class_names[index].strip()  # Strip any leading/trailing whitespace
            confidence_score = prediction[0][index]

            # Suggest medication if disease detected
            medication = medications.get(class_name, None)

            # Convert image to base64 for rendering on the webpage
            img_byte_array = io.BytesIO()
            image.save(img_byte_array, format="PNG")
            img_data = base64.b64encode(img_byte_array.getvalue()).decode("utf-8")

            return render_template("s3.html", prediction=class_name, confidence=confidence_score, medication=medication, img_data=img_data)
        else:
            return render_template("s3.html", error="Model not available or file processing error")

    return render_template("s3.html", prediction=prediction, confidence=confidence, medication=medication, img_data=img_data)

@app.route("/information")
def information():
    return render_template("information.html")

@app.route("/latest-innovations")
def latest_innovations():
    return render_template("latest-innovations.html")

@app.route("/govt-schemes")
def govt_schemes():
    return render_template("govt-schemes.html")

@app.route("/veterinary_map")
def veterinary_map():
    return render_template("veterinary_map.html")

if __name__ == "__main__":
    app.run(debug=True)