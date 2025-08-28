from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import base64
from datetime import datetime
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Create directories for storing images
os.makedirs('auto_captures', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture', methods=['POST'])
def capture_image():
    try:
        data = request.json
        
        # Extract image data from base64
        image_data = data['image'].split(',')[1]  # Remove data URL prefix
        message = data.get('message', 'No message')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Convert base64 to image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Add timestamp and message to image (optional)
        cv2.putText(img, f"Msg: {message}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(img, f"Time: {timestamp}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Generate filename
        filename = f"auto_capture_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
        filepath = os.path.join('auto_captures', filename)
        
        # Save image
        cv2.imwrite(filepath, img)
        
        print(f"✅ Auto-capture saved: {filename}")
        print(f"   Message: {message}")
        print(f"   Timestamp: {timestamp}")
        
        return jsonify({
            'success': True, 
            'filename': filename,
            'saved_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error saving auto-capture: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory('auto_captures', filename)

@app.route('/list_captures')
def list_captures():
    try:
        images = [f for f in os.listdir('auto_captures') if f.endswith(('.jpg', '.png', '.jpeg'))]
        return jsonify({'captures': images, 'count': len(images)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_all', methods=['POST'])
def delete_all_captures():
    try:
        for filename in os.listdir('auto_captures'):
            filepath = os.path.join('auto_captures', filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        return jsonify({'success': True, 'message': 'All captures deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Educational Auto-Capture Webcam Server...")
    print("📁 Captures will be saved in: auto_captures/")
    print("🌐 Open: http://localhost:5000")
    print("⚠️  FOR EDUCATIONAL PURPOSES ONLY!")
    print("⚠️  Always get permission before using!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)