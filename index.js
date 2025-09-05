document.addEventListener('DOMContentLoaded', () => {
    const videoContainer = document.getElementById('video-container');
    const captureButton = document.getElementById('captureButton');
    const recommendButton = document.getElementById('recommendButton');

    let localStream;

    // Function to handle the video stream
    async function handleStream(stream) {
        localStream = stream;
        const video = document.createElement('video');
        video.srcObject = stream;
        video.autoplay = true;
        videoContainer.appendChild(video);
    }

    function captureEmotion() {
        const videoTrack = localStream.getVideoTracks()[0];
        const existingVideo = document.getElementById('video-capture');
    
        // Check if an existing video element is present
        if (existingVideo && existingVideo.parentNode) {
            // Stop the existing video track
            const existingStream = existingVideo.srcObject;
            const tracks = existingStream.getTracks();
            tracks.forEach(track => track.stop());
    
            // Remove the existing video element
            existingVideo.parentNode.removeChild(existingVideo);
        }
    
        // Create a new video element
        const video = document.createElement('video');
        video.id = 'video-capture';
        video.srcObject = new MediaStream([videoTrack]);
        video.autoplay = true;
    
        // Wait for the video to be loaded and play
        video.onloadedmetadata = () => {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
            // Convert the canvas image to frame data
            const imageData = context.getImageData(0, 0, canvas.width, canvas.height).data;
            const frameData = Array.from(imageData);
            // Post request to the server
            fetch('/get_emotion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    frame: frameData,
                }),
            })
            .then(response => response.json())
            .then(data => {
                const processedEmotion = data.processed_frame;
    
                // Log the captured emotion to the console
                console.log('Captured Emotion:', processedEmotion);
    
                // Display or store the captured emotion data
                const emotionDataElement = document.getElementById('emotionData');
                emotionDataElement.innerText = `Captured Emotion: ${processedEmotion}`;
            })
            .catch(error => console.error('Error capturing emotion:', error));
        };
    
    
        // Append the video element to the body to trigger loading
        document.body.appendChild(video);
    }
    

    // Function to recommend songs (replace with your logic)
    function recommendSongs() {
        // Assuming you have input fields with IDs "languageInput" and "singerInput"
        const langInput = document.getElementById('languageInput').value;
        const singerInput = document.getElementById('singerInput').value;
        const emotionDataElement = document.getElementById('emotionData');
        const emotionData = emotionDataElement.innerText;
        // Check if emotion is captured
        if (!emotionData) {
            console.error('Please capture your emotion first.');
            return;
        }

        // Formulate the query
        const query = `${langInput}%20${emotionData}%20${singerInput.split(' ')[0]}%20${singerInput.split(' ')[1]}%20songs`;

        // Open Spotify search page with the formulated query
        window.open(`https://open.spotify.com/search/${query}`, '_blank');

        // Reset emotion data
        document.getElementById('emotionData').innerText = '';
        console.log('Resetting emotion data...');

        // Clear the input fields for language and singer
        document.getElementById('languageInput').value = '';
        document.getElementById('singerInput').value = '';
    }

    // Event listener for the Capture Emotion button
    captureButton.addEventListener('click', () => {
        captureEmotion();
    });

    // Event listener for the Recommend Songs button
    recommendButton.addEventListener('click', () => {
        recommendSongs();
    });

    // Access the user's webcam and start streaming
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(handleStream)
        .catch(error => console.error('Error accessing webcam:', error));
});